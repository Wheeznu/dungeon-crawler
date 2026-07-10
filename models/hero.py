from models.entity import Entity

class Hero(Entity):
    def __init__(self, hero_id: str, name: str, level: int, max_hp: int, atk: int, def_stat: int, spd: int, aggro: int, role: str):
        super().__init__(name, level, max_hp, atk, def_stat, spd, aggro)
        self.hero_id = hero_id
        self.role = role
        self.xp = 0
        self.xp_to_next = 100
        
        self.equipped = {
            "HELM": None,
            "ARMOR": None,
            "GLOVES": None,
            "BOOTS": None,
            "RING": None,
            "NECKLACE": None,
            "MAIN_WEAPON": None,
            "SECONDARY_WEAPON": None
        }
        
        self.unlocked_skills = [] # list of Skill objects
        self.equipped_skills = [] # max 3 Skill objects
        self.basic_attack = None  # Skill object
        
    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next
        self.xp_to_next = int(self.xp_to_next * 1.5)
        # Base stat increase
        self.max_hp += 10
        self.hp = self.max_hp
        self.atk += 2
        self.def_stat += 2
        self.spd += 1
