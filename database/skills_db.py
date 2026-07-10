from models.skill import Skill, TargetType, EffectType

SKILL_DB = {
    # Basic Attacks
    "atk_warrior": {"name": "Basic Attack", "action_cost": 1000, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.0, "element": "Physical", "desc": "Serangan dasar. Memberikan 100% damage fisik."},
    "atk_mage": {"name": "Staff Bonk", "action_cost": 1000, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 0.5, "element": "Physical", "desc": "Pukulan lemah dengan tongkat sihir."},
    "atk_priest": {"name": "Basic Smite", "action_cost": 1000, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 0.8, "element": "Holy", "desc": "Serangan suci ringan."},
    "atk_rogue": {"name": "Quick Stab", "action_cost": 800, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.0, "element": "Physical", "desc": "Serangan cepat dengan belati."},

    # Common Skills
    "Slash": {"name": "Slash", "action_cost": 1200, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.5, "element": "Physical", "desc": "[SINGLE] Tebasan kuat (150% DMG)."},
    "Taunt": {"name": "Taunt", "action_cost": 800, "target_type": TargetType.SELF, "effect_type": EffectType.HEAL, "power": 0.0, "element": "Neutral", "desc": "[SELF] Memancing musuh."},
    "Fireball": {"name": "Fireball", "action_cost": 1300, "target_type": TargetType.BLAST, "effect_type": EffectType.DAMAGE, "power": 1.8, "element": "Fire", "desc": "[BLAST] Ledakan api mematikan ke target dan sekitarnya (180% Utama, 50% Area)."},
    "Magic Missile": {"name": "Magic Missile", "action_cost": 1000, "target_type": TargetType.ALL_ENEMIES, "effect_type": EffectType.DAMAGE, "power": 0.8, "element": "Magic", "desc": "[AoE] Tembakan sihir menyebar ke seluruh musuh (80% DMG)."},
    "Heal": {"name": "Heal", "action_cost": 1200, "target_type": TargetType.ALLY, "effect_type": EffectType.HEAL, "power": 2.0, "element": "Holy", "desc": "[SINGLE-ALLY] Memulihkan HP target."},
    "Smite": {"name": "Smite", "action_cost": 1500, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 2.0, "element": "Holy", "desc": "[SINGLE] Cahaya suci mematikan (200% DMG)."},
    "Backstab": {"name": "Backstab", "action_cost": 1400, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 2.5, "element": "Physical", "desc": "[SINGLE] Serangan fatal dari belakang (250% DMG)."},
    "Poison Strike": {"name": "Poison Strike", "action_cost": 1100, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.2, "element": "Poison", "desc": "[SINGLE] Menyuntikkan racun (120% DMG)."},
    "Holy Strike": {"name": "Holy Strike", "action_cost": 1600, "target_type": TargetType.ALL_ENEMIES, "effect_type": EffectType.DAMAGE, "power": 1.3, "element": "Holy", "desc": "[AoE] Gelombang suci ke seluruh musuh (130% DMG)."},
    "Double Shot": {"name": "Double Shot", "action_cost": 1300, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.9, "element": "Physical", "desc": "[SINGLE] 2 anak panah beruntun (190% DMG)."}
}

def get_skill(skill_id: str, level: int = 1) -> Skill:
    data = SKILL_DB.get(skill_id)
    if not data:
        data = {"name": skill_id, "action_cost": 1000, "target_type": TargetType.SINGLE_ENEMY, "effect_type": EffectType.DAMAGE, "power": 1.0, "element": "Neutral", "desc": "Skill tidak diketahui."}
    return Skill(skill_id, data["name"], level, data["action_cost"], data["target_type"], data["effect_type"], data["power"], data["element"], data["desc"])
