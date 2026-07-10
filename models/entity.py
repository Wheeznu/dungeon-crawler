class Entity:
    def __init__(self, name: str, level: int, max_hp: int, atk: int, def_stat: int, spd: int, aggro: int):
        self.name = name
        self.level = level
        self.max_hp = max_hp
        self.hp = max_hp
        self.atk = atk
        self.def_stat = def_stat
        self.spd = spd
        self.aggro = aggro
        
        self.action_points = 0
        self.status_effects = [] # dicts of {'type': 'poison', 'duration': 3, 'value': 5}
        self.is_guarding = False
        
    def take_damage(self, amount: int):
        if self.is_guarding:
            amount = max(1, amount // 2)
        self.hp -= max(1, amount)
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)

    @property
    def is_dead(self):
        return self.hp <= 0
