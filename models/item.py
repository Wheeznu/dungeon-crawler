from enum import Enum

class ItemType(Enum):
    CONSUMABLE = 1
    MAIN_WEAPON = 2
    SECONDARY_WEAPON = 3
    HELM = 4
    ARMOR = 5
    GLOVES = 6
    BOOTS = 7
    RING = 8
    NECKLACE = 9

class Rarity(Enum):
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5

class Item:
    def __init__(self, item_id: str, name: str, item_type: ItemType, rarity: Rarity, 
                 value: int, stat_modifiers: dict = None, use_effect: dict = None, usable_by: list = None):
        self.id = item_id
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.value = value
        self.stat_modifiers = stat_modifiers or {}
        self.use_effect = use_effect or {}
        self.usable_by = usable_by
