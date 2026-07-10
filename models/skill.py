from enum import Enum

class TargetType(Enum):
    SINGLE_ENEMY = 1
    ALL_ENEMIES = 2
    ALLY = 3
    ALL_ALLIES = 4
    SELF = 5
    BLAST = 6

class EffectType(Enum):
    DAMAGE = 1
    HEAL = 2
    BUFF = 3
    DEBUFF = 4

class Skill:
    def __init__(self, skill_id: str, name: str, level: int, action_cost: int, 
                 target_type: TargetType, effect_type: EffectType, power_multiplier: float,
                 element: str = "Neutral", description: str = ""):
        self.id = skill_id
        self.name = name
        self.level = level
        self.action_cost = action_cost  # AP delay
        self.target_type = target_type
        self.effect_type = effect_type
        self.power_multiplier = power_multiplier
        self.element = element
        self.description = description

    def upgrade(self):
        self.level += 1
        self.power_multiplier += 0.2
