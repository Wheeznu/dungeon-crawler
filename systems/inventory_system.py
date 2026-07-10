from models.item import ItemType

class InventorySystem:
    def __init__(self):
        self.items = []
        
    def add_item(self, item):
        self.items.append(item)
        
    def equip_hero(self, hero, item):
        slot = item.item_type.name
        old = hero.equipped.get(slot)
        hero.equipped[slot] = item
        self._apply_stats(hero, item, old)
        if old: self.items.append(old)
        if item in self.items: self.items.remove(item)
            
    def unequip_hero(self, hero, slot):
        old = hero.equipped.get(slot)
        if old:
            hero.equipped[slot] = None
            self._apply_stats(hero, None, old)
            self.items.append(old)
            
    def _apply_stats(self, hero, new_item, old_item):
        if old_item:
            for stat, val in old_item.stat_modifiers.items():
                if stat == "ATK": hero.atk -= val
                if stat == "DEF": hero.def_stat -= val
                if stat == "SPD": hero.spd -= val
                if stat == "MAXHP":
                    hero.max_hp -= val
                    hero.hp = min(hero.hp, hero.max_hp)
                    
        if new_item:
            for stat, val in new_item.stat_modifiers.items():
                if stat == "ATK": hero.atk += val
                if stat == "DEF": hero.def_stat += val
                if stat == "SPD": hero.spd += val
                if stat == "MAXHP": hero.max_hp += val
