from models.enemy import Enemy
from database.skills_db import get_skill
from systems.config import config
import random

ENEMY_TEMPLATES = {
    # TIER 1 (Floor 1-30)
    "Slime": {"max_hp": 30, "atk": 5, "def": 1, "spd": 50, "skills": [], "tier": 1, "icon": "○"},
    "Goblin": {"max_hp": 45, "atk": 8, "def": 2, "spd": 80, "skills": ["Slash"], "tier": 1, "icon": "▲"},
    "Wolf": {"max_hp": 40, "atk": 10, "def": 1, "spd": 110, "skills": [], "tier": 1, "icon": "♜"},
    
    # TIER 2 (Floor 31-70)
    "Orc": {"max_hp": 100, "atk": 15, "def": 5, "spd": 70, "skills": ["Slash", "Taunt"], "tier": 2, "icon": "■"},
    "Skeleton": {"max_hp": 60, "atk": 12, "def": 8, "spd": 85, "skills": ["Poison Strike"], "tier": 2, "icon": "☠"},
    "Gargoyle": {"max_hp": 150, "atk": 18, "def": 12, "spd": 60, "skills": ["Slash"], "tier": 2, "icon": "♆"},
    
    # TIER 3 (Floor 71-99)
    "Dark Knight": {"max_hp": 250, "atk": 35, "def": 15, "spd": 90, "skills": ["Slash", "Smite"], "tier": 3, "icon": "♟"},
    "Dragon Whelp": {"max_hp": 220, "atk": 40, "def": 10, "spd": 100, "skills": ["Fireball"], "tier": 3, "icon": "⋈"},
    "Lich": {"max_hp": 180, "atk": 45, "def": 5, "spd": 110, "skills": ["Fireball", "Poison Strike"], "tier": 3, "icon": "☗"},
    
    # BOSSES
    "Boss_Ogre": {"max_hp": 500, "atk": 50, "def": 20, "spd": 60, "skills": ["Slash", "Taunt"], "tier": 4, "icon": "⛑"},
    "Boss_Demon": {"max_hp": 1500, "atk": 100, "def": 50, "spd": 90, "skills": ["Fireball", "Smite"], "tier": 4, "icon": "⛧"},
    "Boss_Dragon": {"max_hp": 3000, "atk": 200, "def": 80, "spd": 120, "skills": ["Fireball", "Holy Strike", "Slash"], "tier": 4, "icon": "♛"}
}

def get_waves_for_floor(floor_level: int) -> list:
    is_boss = (floor_level % 10 == 0)
    num_waves = 1 if is_boss else (2 if floor_level < 30 else 3)
    waves = []
    
    for wave_idx in range(num_waves):
        enemies = []
        num_enemies = 1 if is_boss else random.randint(2, 5)
        
        for i in range(num_enemies):
            if is_boss:
                if floor_level <= 30: pool = ["Boss_Ogre"]
                elif floor_level <= 80: pool = ["Boss_Demon"]
                else: pool = ["Boss_Dragon"]
            else:
                if floor_level <= 30: pool = [k for k, v in ENEMY_TEMPLATES.items() if v["tier"] == 1]
                elif floor_level <= 70: pool = [k for k, v in ENEMY_TEMPLATES.items() if v["tier"] == 2]
                else: pool = [k for k, v in ENEMY_TEMPLATES.items() if v["tier"] == 3]
                
            t_name = random.choice(pool)
            data = ENEMY_TEMPLATES[t_name]
            
            diff_mult = 1.0
            if config["difficulty"] == "EASY": diff_mult = 0.75
            elif config["difficulty"] == "HARD": diff_mult = 1.5
            
            scale_hp = int(data["max_hp"] * (1 + (floor_level * 0.15)) * diff_mult)
            scale_atk = int(data["atk"] * (1 + (floor_level * 0.1)) * diff_mult)
            scale_def = int(data["def"] * (1 + (floor_level * 0.1)) * diff_mult)
            
            e = Enemy(
                enemy_id=f"e_{floor_level}_{wave_idx}_{i}", 
                name=t_name, 
                level=floor_level, 
                max_hp=scale_hp, 
                atk=scale_atk, 
                def_stat=scale_def, 
                spd=data["spd"],
                aggro=10,
                ai_type="BASIC",
                xp_reward=floor_level * 10,
                drop_chance=0.5
            )
            e.name = f"{data.get('icon', '👾')} {e.name}"
            e.unlocked_skills = [get_skill(s) for s in data["skills"]]
            e.equipped_skills = e.unlocked_skills[:3]
            e.basic_attack = get_skill("atk_warrior")
            
            enemies.append(e)
            
        waves.append(enemies)
        
    return waves
