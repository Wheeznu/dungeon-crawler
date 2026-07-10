import random
from models.item import Rarity
from database.items_db import get_base_item, BASE_ITEMS

def generate_loot(floor_level: int, roster: list, is_boss: bool = False):
    drop_chance = 1.0
    if random.random() > drop_chance:
        return None
        
    roster_roles = {h.role for h in roster}
    valid_items = []
    for item_id, data in BASE_ITEMS.items():
        if data.get("usable_by") is None:
            valid_items.append(item_id)
        else:
            if any(role in data["usable_by"] for role in roster_roles):
                valid_items.append(item_id)
                
    if not valid_items:
        return None
        
    item_id = random.choice(valid_items)
    
    roll = random.random()
    if is_boss:
        # Bosses drop high rarity items guaranteed
        if roll < 0.5: rarity = Rarity.RARE
        elif roll < 0.8: rarity = Rarity.EPIC
        else: rarity = Rarity.LEGENDARY
    else:
        # Normal enemies drop scale slightly with floor level, adjusted for 100% drop rate
        floor_bonus = floor_level / 1000.0 # max 0.1 at floor 100
        
        if roll < (0.005 + floor_bonus): rarity = Rarity.LEGENDARY
        elif roll < (0.025 + floor_bonus * 2): rarity = Rarity.EPIC
        elif roll < (0.10 + floor_bonus * 3): rarity = Rarity.RARE
        elif roll < 0.40: rarity = Rarity.UNCOMMON
        else: rarity = Rarity.COMMON
        
    return get_base_item(item_id, rarity, floor_level)
