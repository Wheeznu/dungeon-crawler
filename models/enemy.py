from models.entity import Entity

class Enemy(Entity):
    def __init__(self, enemy_id: str, name: str, level: int, max_hp: int, atk: int, def_stat: int, spd: int, aggro: int, ai_type: str, xp_reward: int, drop_chance: float):
        super().__init__(name, level, max_hp, atk, def_stat, spd, aggro)
        self.enemy_id = enemy_id
        self.ai_type = ai_type
        self.xp_reward = xp_reward
        self.drop_chance = drop_chance # 0.0 to 1.0
        self.skills = [] # Skills for advanced enemies
