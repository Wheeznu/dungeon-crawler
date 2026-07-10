from models.item import Item, ItemType, Rarity

BASE_ITEMS = {}

# 1. GENERATE MAIN WEAPONS (Class Restricted)
WPN_TIERS = [
    ("bronze", "Perunggu", 10),
    ("iron", "Besi", 18),
    ("steel", "Baja", 28),
    ("mithril", "Mithril", 40),
    ("adamantite", "Adamantite", 55),
    ("obsidian", "Obsidian", 75),
    ("dragon", "Tulang Naga", 100)
]

MAIN_WPN_TYPES = [
    ("sword", "Pedang", 1.0, ["WARRIOR", "PALADIN", "SAMURAI", "BERSERKER"]),
    ("dagger", "Belati", 0.7, ["ROGUE", "ASSASSIN"]),
    ("staff", "Tongkat", 1.2, ["MAGE", "NECROMANCER", "SORCERER"]),
    ("bow", "Busur", 0.9, ["RANGER", "BARD"]),
    ("mace", "Gada", 1.1, ["PRIEST", "DRUID", "MONK"]),
    ("flask", "Botol Kimia", 0.8, ["ALCHEMIST"])
]

for mat_id, mat_name, mat_base in WPN_TIERS:
    for typ_id, typ_name, mult, classes in MAIN_WPN_TYPES:
        item_id = f"mwpn_{mat_id}_{typ_id}"
        BASE_ITEMS[item_id] = {
            "name": f"{typ_name} {mat_name}",
            "type": ItemType.MAIN_WEAPON,
            "base_val": int(mat_base * mult),
            "stat": "ATK",
            "usable_by": classes
        }

# 2. GENERATE SECONDARY WEAPONS (Class Restricted)
SEC_WPN_TYPES = [
    ("shield", "Perisai", 0.8, ["WARRIOR", "PALADIN"]),
    ("orb", "Orb Sihir", 1.0, ["MAGE", "NECROMANCER", "SORCERER"]),
    ("quiver", "Tabung Panah", 0.6, ["RANGER", "BARD"]),
    ("relic", "Relik Suci", 0.9, ["PRIEST", "DRUID", "MONK"]),
    ("scd_dagger", "Belati Kiri", 0.6, ["ROGUE", "ASSASSIN"]),
    ("bracer", "Gelang Tangan", 0.5, ["SAMURAI", "BERSERKER"]),
    ("bomb", "Kantong Bom", 0.7, ["ALCHEMIST"])
]

for mat_id, mat_name, mat_base in WPN_TIERS:
    for typ_id, typ_name, mult, classes in SEC_WPN_TYPES:
        item_id = f"swpn_{mat_id}_{typ_id}"
        # For secondary weapons, they might give DEF (Shield) or ATK (Orb/Dagger)
        stat = "DEF" if typ_id in ["shield", "bracer"] else "ATK"
        val = int(mat_base * mult)
        if stat == "DEF": val = int(val * 1.5) # Boost def value slightly
        BASE_ITEMS[item_id] = {
            "name": f"{typ_name} {mat_name}",
            "type": ItemType.SECONDARY_WEAPON,
            "base_val": val,
            "stat": stat,
            "usable_by": classes
        }

# 3. GENERATE GENERIC ARMOR & ACCESSORIES
ARM_TIERS = [
    ("rags", "Kain Jelek", 5),
    ("leather", "Kulit", 12),
    ("chainmail", "Zirah Rantai", 20),
    ("plate", "Zirah Plat", 35),
    ("mithril", "Mithril", 50),
    ("obsidian", "Obsidian", 70),
    ("dragon", "Naga", 95)
]

ARM_SLOTS = [
    ("helm", "Helm", ItemType.HELM, 0.6),
    ("arm", "Zirah", ItemType.ARMOR, 1.0),
    ("glv", "Sarung Tangan", ItemType.GLOVES, 0.4),
    ("bts", "Sepatu", ItemType.BOOTS, 0.5)
]

for mat_id, mat_name, mat_base in ARM_TIERS:
    for slot_id, slot_name, item_type, mult in ARM_SLOTS:
        item_id = f"{slot_id}_{mat_id}"
        BASE_ITEMS[item_id] = {
            "name": f"{slot_name} {mat_name}",
            "type": item_type,
            "base_val": int(mat_base * mult),
            "stat": "DEF",
            "usable_by": None
        }

ACC_TIERS = [
    ("copper", "Tembaga", 8),
    ("silver", "Perak", 15),
    ("gold", "Emas", 25),
    ("plat", "Platinum", 40),
    ("diamond", "Berlian", 60)
]

ACC_SLOTS = [
    ("rng", "Cincin", ItemType.RING, "ATK", 0.5),
    ("nck", "Kalung", ItemType.NECKLACE, "MAXHP", 5.0) # Necklaces give HP
]

for mat_id, mat_name, mat_base in ACC_TIERS:
    for slot_id, slot_name, item_type, stat, mult in ACC_SLOTS:
        item_id = f"{slot_id}_{mat_id}"
        BASE_ITEMS[item_id] = {
            "name": f"{slot_name} {mat_name}",
            "type": item_type,
            "base_val": int(mat_base * mult),
            "stat": stat,
            "usable_by": None
        }

# 4. Consumables
BASE_ITEMS["pot_health_small"] = {"name": "Ramuan Penyembuh Kecil", "type": ItemType.CONSUMABLE, "base_val": 50, "effect": "HEAL", "usable_by": None}
BASE_ITEMS["pot_health_medium"] = {"name": "Ramuan Penyembuh Sedang", "type": ItemType.CONSUMABLE, "base_val": 150, "effect": "HEAL", "usable_by": None}
BASE_ITEMS["pot_health_large"] = {"name": "Ramuan Penyembuh Besar", "type": ItemType.CONSUMABLE, "base_val": 350, "effect": "HEAL", "usable_by": None}
BASE_ITEMS["pot_health_elixir"] = {"name": "Elixir Kehidupan", "type": ItemType.CONSUMABLE, "base_val": 1000, "effect": "HEAL", "usable_by": None}

def get_base_item(item_id: str, rarity: Rarity, floor_level: int) -> Item:
    data = BASE_ITEMS.get(item_id)
    if not data:
        return None
        
    multiplier_map = {
        Rarity.COMMON: 1.0,
        Rarity.UNCOMMON: 1.2,
        Rarity.RARE: 1.5,
        Rarity.EPIC: 2.0,
        Rarity.LEGENDARY: 3.0
    }
    
    stat_val = int(data["base_val"] * multiplier_map[rarity] * (1 + (floor_level * 0.05)))
    
    modifiers = {}
    use_effect = {}
    if data["type"] != ItemType.CONSUMABLE:
        modifiers[data["stat"]] = stat_val
    else:
        use_effect[data["effect"]] = stat_val
        
    rarity_names = {
        Rarity.COMMON: "",
        Rarity.UNCOMMON: "Uncommon ",
        Rarity.RARE: "Rare ",
        Rarity.EPIC: "Epic ",
        Rarity.LEGENDARY: "Legendary "
    }
    prefix = rarity_names.get(rarity, "")
    
    unique_id = f"{item_id}_{floor_level}"
    # Item(item_id, name, item_type, rarity, value, stat_modifiers, use_effect, usable_by)
    # The value is the sell price (e.g., base_val * multiplier * 2)
    sell_price = int(data["base_val"] * multiplier_map[rarity]) * 5
    
    return Item(
        unique_id, 
        f"{prefix}{data['name']}", 
        data["type"], 
        rarity, 
        sell_price, 
        modifiers, 
        use_effect,
        data.get("usable_by")
    )
