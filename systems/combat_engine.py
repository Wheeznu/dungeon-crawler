import random
from models.skill import TargetType, EffectType

class CombatEngine:
    def __init__(self, heroes, enemies, ui_event_queue):
        self.heroes = heroes
        self.enemies = enemies
        self.ui_event_queue = ui_event_queue
        
    @property
    def active_entities(self):
        return [h for h in self.heroes if not h.is_dead] + [e for e in self.enemies if not e.is_dead]
        
    def tick(self):
        # Action Gauge accumulation
        for entity in self.active_entities:
            entity.action_points += entity.spd
            if entity.action_points >= 1000:
                return entity # Entity gets a turn
        return None
        
    def execute_action(self, actor, skill, target):
        actor.action_points -= skill.action_cost
        
        targets_with_mults = []
        if skill.target_type in [TargetType.SINGLE_ENEMY, TargetType.ALLY, TargetType.SELF]:
            if target and not target.is_dead:
                targets_with_mults = [(target, 1.0)]
        elif skill.target_type == TargetType.ALL_ENEMIES:
            pool = [e for e in self.enemies if not e.is_dead] if actor in self.heroes else [h for h in self.heroes if not h.is_dead]
            targets_with_mults = [(t, 1.0) for t in pool]
        elif skill.target_type == TargetType.ALL_ALLIES:
            pool = [h for h in self.heroes if not h.is_dead] if actor in self.heroes else [e for e in self.enemies if not e.is_dead]
            targets_with_mults = [(t, 1.0) for t in pool]
        elif skill.target_type == TargetType.BLAST:
            pool = [e for e in self.enemies if not e.is_dead] if actor in self.heroes else [h for h in self.heroes if not h.is_dead]
            if target and not target.is_dead and target in pool:
                idx = pool.index(target)
                targets_with_mults.append((target, 1.0))
                if idx > 0: targets_with_mults.append((pool[idx-1], 0.5))
                if idx < len(pool) - 1: targets_with_mults.append((pool[idx+1], 0.5))
            
        for t, mult in targets_with_mults:
            if skill.effect_type == EffectType.DAMAGE:
                damage = int(max(1, (actor.atk * skill.power_multiplier * mult) - (t.def_stat / 2)))
                # RNG variation
                damage = int(damage * random.uniform(0.9, 1.1))
                
                # Critical hit (5% base)
                is_crit = random.random() < 0.05
                if is_crit:
                    damage = int(damage * 1.5)
                    
                t.take_damage(damage)
                
                self.ui_event_queue.append({
                    "type": "DAMAGE",
                    "source": actor.name,
                    "target": t.name,
                    "value": damage,
                    "is_crit": is_crit,
                    "element": skill.element
                })
            elif skill.effect_type == EffectType.HEAL:
                heal_amt = int(actor.atk * skill.power_multiplier * mult)
                t.heal(heal_amt)
                self.ui_event_queue.append({
                    "type": "HEAL",
                    "source": actor.name,
                    "target": t.name,
                    "value": heal_amt
                })

    def run_ai_turn(self, enemy):
        # Enemy selects target based on highest aggro + some RNG
        alive_heroes = [h for h in self.heroes if not h.is_dead]
        if not alive_heroes:
            return
            
        # Weighted random choice based on aggro
        total_aggro = sum(h.aggro for h in alive_heroes)
        if total_aggro == 0:
            target = random.choice(alive_heroes)
        else:
            r = random.uniform(0, total_aggro)
            curr = 0
            for h in alive_heroes:
                curr += h.aggro
                if r <= curr:
                    target = h
                    break
            else:
                target = alive_heroes[-1]
                
        # Basic attack for now (Mock basic attack skill)
        from models.skill import Skill
        basic_attack = Skill("enemy_atk", "Strike", 1, 1000, TargetType.SINGLE_ENEMY, EffectType.DAMAGE, 1.0)
        self.execute_action(enemy, basic_attack, target)
        
    def run_auto_battle(self, hero):
        from models.skill import EffectType, TargetType
        
        alive_enemies = [e for e in self.enemies if not e.is_dead]
        alive_heroes = [h for h in self.heroes if not h.is_dead]
        
        if not alive_enemies:
            return
            
        # Helper: Calculate potential damage
        def calc_dmg(skill, target, mult=1.0):
            return max(1, (hero.atk * skill.power_multiplier * mult) - (target.def_stat / 2))
            
        # Prioritas 1: Heal hero sekarat (HP < 35%)
        critical_heroes = [h for h in alive_heroes if (h.hp / max(1, h.max_hp)) < 0.35]
        if critical_heroes:
            critical_heroes.sort(key=lambda h: h.hp / max(1, h.max_hp)) # Paling sekarat duluan
            heal_skills = [s for s in hero.equipped_skills if s.effect_type == EffectType.HEAL and hero.action_points >= s.action_cost]
            if heal_skills:
                skill = heal_skills[0] # Pakai heal pertama
                target = critical_heroes[0]
                self.execute_action(hero, skill, target)
                return
                
        # Prioritas 2: Cek Lethal Damage (Kill Steal / Finishing Move)
        # Cari musuh yang bisa dibunuh HANYA dengan Basic Attack
        if hero.action_points >= hero.basic_attack.action_cost:
            for e in alive_enemies:
                if calc_dmg(hero.basic_attack, e) >= e.hp:
                    self.execute_action(hero, hero.basic_attack, e)
                    return
        # Cari musuh yang bisa dibunuh dengan skill single-target terkuat
        single_dmg_skills = [s for s in hero.equipped_skills if s.target_type == TargetType.SINGLE_ENEMY and hero.action_points >= s.action_cost and s.effect_type == EffectType.DAMAGE]
        if single_dmg_skills:
            best_single_skill = max(single_dmg_skills, key=lambda s: s.power_multiplier)
            for e in alive_enemies:
                if calc_dmg(best_single_skill, e) >= e.hp:
                    self.execute_action(hero, best_single_skill, e)
                    return
                
        # Prioritas 3: AoE vs Single Target efisiensi
        best_aoe_skill = None
        aoe_total_dmg = 0
        aoe_skills = [s for s in hero.equipped_skills if s.target_type == TargetType.ALL_ENEMIES and hero.action_points >= s.action_cost and s.effect_type == EffectType.DAMAGE]
        if aoe_skills:
            best_aoe_skill = max(aoe_skills, key=lambda s: s.power_multiplier)
            aoe_total_dmg = sum(calc_dmg(best_aoe_skill, e) for e in alive_enemies)
            
        best_single_target = min(alive_enemies, key=lambda e: e.hp) # Fokus HP terendah
        best_single_dmg = 0
        if single_dmg_skills:
            best_single_dmg = calc_dmg(best_single_skill, best_single_target)
            
        if best_aoe_skill and aoe_total_dmg > best_single_dmg * 1.5:
            # Gunakan AoE jika damage totalnya 1.5x lebih besar dari damage single target terkuat
            self.execute_action(hero, best_aoe_skill, alive_enemies)
            return
            
        # Prioritas 4: Single Target terkuat ke musuh HP terendah
        if single_dmg_skills:
            self.execute_action(hero, best_single_skill, best_single_target)
            return
            
        # Prioritas 5: Basic Attack
        if hero.action_points >= hero.basic_attack.action_cost:
            self.execute_action(hero, hero.basic_attack, best_single_target)
        else:
            # Skip turn secara aman dengan mengurangi AP 
            # Note: Ini harusnya tidak terjadi jika basic attack cost = 1000 dan max AP = 1000.
            # Namun untuk mencegah infinite loop, kita paksa kurangi.
            hero.action_points -= 1000

    def check_victory(self):
        heroes_alive = any(not h.is_dead for h in self.heroes)
        enemies_alive = any(not e.is_dead for e in self.enemies)
        if not heroes_alive:
            return "DEFEAT"
        if not enemies_alive:
            return "VICTORY"
        return "ONGOING"
