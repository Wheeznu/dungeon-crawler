import json
import os
from database.items_db import get_base_item
from models.item import Rarity

def get_save_file(slot_number):
    return f"save_{slot_number}.json"

def save_game(roster, gold, current_floor, inventory_items, slot_number=1):
    data = {
        "gold": gold,
        "current_floor": current_floor,
        "roster": [],
        "inventory": []
    }
    for hero in roster:
        equipped_data = {}
        for slot, item in hero.equipped.items():
            if item:
                parts = item.id.split('_')
                base_id = "_".join(parts[:-1])
                equipped_data[slot] = {
                    "base_id": base_id,
                    "rarity": item.rarity.value,
                    "floor_level": int(parts[-1]) if parts[-1].isdigit() else current_floor
                }
            else:
                equipped_data[slot] = None

        data["roster"].append({
            "hero_id": hero.hero_id,
            "name": hero.name,
            "level": hero.level,
            "xp": hero.xp,
            "hp": hero.hp,
            "max_hp": hero.max_hp,
            "atk": hero.atk,
            "def_stat": hero.def_stat,
            "spd": hero.spd,
            "aggro": hero.aggro,
            "role": hero.role,
            "equipped": equipped_data
        })
        
    for item in inventory_items:
        parts = item.id.split('_')
        base_id = "_".join(parts[:-1])
        floor_level = int(parts[-1]) if parts[-1].isdigit() else current_floor
        data["inventory"].append({
            "base_id": base_id,
            "rarity": item.rarity.value,
            "floor_level": floor_level
        })
        
    with open(get_save_file(slot_number), "w") as f:
        json.dump(data, f, indent=4)
        
def load_game(slot_number=1):
    save_file = get_save_file(slot_number)
    if not os.path.exists(save_file):
        return None
    try:
        with open(save_file, "r") as f:
            return json.load(f)
    except:
        return None

def get_save_info(slot_number):
    save_file = get_save_file(slot_number)
    if not os.path.exists(save_file):
        return {"exists": False}
    try:
        with open(save_file, "r") as f:
            data = json.load(f)
            return {
                "exists": True,
                "gold": data.get("gold", 0),
                "floor": data.get("current_floor", 1),
                "heroes": len(data.get("roster", []))
            }
    except:
        return {"exists": False}

def check_save_slots():
    for i in range(1, 4):
        if os.path.exists(get_save_file(i)):
            return True
    return False
