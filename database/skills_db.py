from models.skill import Skill, TargetType, EffectType

SKILL_DB = {
    # Basic Attacks
    "atk_warrior": {"name": "Basic Attack", "action_cost": 1000, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.0, "element": "Physical", "desc": {"ID": "Serangan dasar. Memberikan 100% damage fisik.", "EN": "Basic attack. Deals 100% physical damage."}},
    "atk_mage": {"name": "Staff Bonk", "action_cost": 1000, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 0.5, "element": "Physical", "desc": {"ID": "Pukulan lemah dengan tongkat sihir.", "EN": "Weak strike with a magic staff."}},
    "atk_priest": {"name": "Basic Smite", "action_cost": 1000, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 0.8, "element": "Holy", "desc": {"ID": "Serangan suci ringan.", "EN": "Light holy strike."}},
    "atk_rogue": {"name": "Quick Stab", "action_cost": 800, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.0, "element": "Physical", "desc": {"ID": "Serangan cepat dengan belati.", "EN": "Quick stab with a dagger."}},

    # Common Skills
    "Slash": {"name": "Slash", "action_cost": 1200, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.5, "element": "Physical", "desc": {"ID": "[SINGLE] Tebasan kuat (150% DMG).", "EN": "[SINGLE] Strong slash (150% DMG)."}},
    "Taunt": {"name": "Taunt", "action_cost": 800, "target_type": TargetType.SELF, "effect_type": EffectType.HEAL, "power": 0.0, "element": "Neutral", "desc": {"ID": "[SELF] Memancing musuh.", "EN": "[SELF] Taunt enemies."}},
    "Fireball": {"name": "Fireball", "action_cost": 1300, "target_type": TargetType.BLAST, "effect_type": EffectType.DAMAGE, "power": 1.8, "element": "Fire", "desc": {"ID": "[BLAST] Ledakan api mematikan ke target dan sekitarnya (180% Utama, 50% Area).", "EN": "[BLAST] Lethal fire explosion to target and surroundings (180% Primary, 50% Splash)."}},
    "Magic Missile": {"name": "Magic Missile", "action_cost": 1000, "target_type": TargetType.ALL_ENEMIES, "effect_type": EffectType.DAMAGE, "power": 0.8, "element": "Magic", "desc": {"ID": "[AoE] Tembakan sihir menyebar ke seluruh musuh (80% DMG).", "EN": "[AoE] Magic shots scattering to all enemies (80% DMG)."}},
    "Heal": {"name": "Heal", "action_cost": 1200, "target_type": TargetType.ALLY, "effect_type": EffectType.HEAL, "power": 2.0, "element": "Holy", "desc": {"ID": "[SINGLE-ALLY] Memulihkan HP target.", "EN": "[SINGLE-ALLY] Restores target's HP."}},
    "Smite": {"name": "Smite", "action_cost": 1500, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 2.0, "element": "Holy", "desc": {"ID": "[SINGLE] Cahaya suci mematikan (200% DMG).", "EN": "[SINGLE] Deadly holy light (200% DMG)."}},
    "Backstab": {"name": "Backstab", "action_cost": 1400, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 2.5, "element": "Physical", "desc": {"ID": "[SINGLE] Serangan fatal dari belakang (250% DMG).", "EN": "[SINGLE] Fatal attack from behind (250% DMG)."}},
    "Poison Strike": {"name": "Poison Strike", "action_cost": 1100, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.2, "element": "Poison", "desc": {"ID": "[SINGLE] Menyuntikkan racun (120% DMG).", "EN": "[SINGLE] Injects poison (120% DMG)."}},
    "Holy Strike": {"name": "Holy Strike", "action_cost": 1600, "target_type": TargetType.ALL_ENEMIES, "effect_type": EffectType.DAMAGE, "power": 1.3, "element": "Holy", "desc": {"ID": "[AoE] Gelombang suci ke seluruh musuh (130% DMG).", "EN": "[AoE] Holy wave to all enemies (130% DMG)."}},
    "Double Shot": {"name": "Double Shot", "action_cost": 1300, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.9, "element": "Physical", "desc": {"ID": "[SINGLE] 2 anak panah beruntun (190% DMG).", "EN": "[SINGLE] 2 arrows in a row (190% DMG)."}}
}

def get_skill(skill_id: str, level: int = 1) -> Skill:
    from systems.config import config
    data = SKILL_DB.get(skill_id)
    lang = config.get("language", "ID")
    if not data:
        desc_text = "Skill tidak diketahui." if lang == "ID" else "Unknown skill."
        data = {"name": skill_id, "action_cost": 1000, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.0, "element": "Neutral", "desc": desc_text}
        
    desc_val = data["desc"].get(lang, data["desc"].get("ID", "")) if isinstance(data["desc"], dict) else data["desc"]
    return Skill(skill_id, data["name"], level, data["action_cost"], data["target_type"], data["effect_type"], data["power"], data["element"], desc_val)
