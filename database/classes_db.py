HERO_ARCHETYPES = {
    "WARRIOR": {"name": "Warrior", "max_hp": 150, "atk": 15, "def": 10, "spd": 80, "aggro": 100, "skills": ["Slash", "Taunt"], "basic": "atk_warrior", "icon": "♞", "desc": "Petarung garis depan dengan keseimbangan menyerang dan bertahan."},
    "MAGE": {"name": "Mage", "max_hp": 80, "atk": 25, "def": 5, "spd": 90, "aggro": 30, "skills": ["Fireball", "Magic Missile"], "basic": "atk_mage", "icon": "★", "desc": "Pengguna sihir mematikan. HP rendah namun damage tinggi."},
    "PRIEST": {"name": "Priest", "max_hp": 100, "atk": 8, "def": 8, "spd": 95, "aggro": 50, "skills": ["Heal", "Smite"], "basic": "atk_priest", "icon": "✚", "desc": "Penyembuh tim yang vital. Pertahanan menengah."},
    "ROGUE": {"name": "Rogue", "max_hp": 90, "atk": 18, "def": 6, "spd": 120, "aggro": 20, "skills": ["Backstab", "Poison Strike"], "basic": "atk_rogue", "icon": "♦", "desc": "Lincah dan mematikan. Sering bergerak duluan di awal giliran."},
    "PALADIN": {"name": "Paladin", "max_hp": 180, "atk": 12, "def": 15, "spd": 75, "aggro": 150, "skills": ["Holy Strike", "Heal"], "basic": "atk_warrior", "icon": "⛨", "desc": "Ksatria suci dengan pertahanan baja dan HP terbanyak."},
    "BARD": {"name": "Bard", "max_hp": 95, "atk": 10, "def": 7, "spd": 110, "aggro": 40, "skills": ["Magic Missile"], "basic": "atk_rogue", "icon": "♪", "desc": "Penyair yang ahli dalam mendukung tim. Lincah."},
    "DRUID": {"name": "Druid", "max_hp": 110, "atk": 14, "def": 9, "spd": 85, "aggro": 60, "skills": ["Poison Strike", "Heal"], "basic": "atk_priest", "icon": "♣", "desc": "Penjaga alam yang seimbang. Bisa menyerang maupun menyembuhkan."},
    "NECROMANCER": {"name": "Necromancer", "max_hp": 85, "atk": 22, "def": 6, "spd": 88, "aggro": 35, "skills": ["Fireball", "Poison Strike"], "basic": "atk_mage", "icon": "☠", "desc": "Penyihir gelap dengan sihir mematikan. Agak lambat."},
    "RANGER": {"name": "Ranger", "max_hp": 100, "atk": 16, "def": 8, "spd": 115, "aggro": 45, "skills": ["Double Shot"], "basic": "atk_rogue", "icon": "➹", "desc": "Pemanah jitu dari jarak jauh. Kecepatan sangat tinggi."},
    "MONK": {"name": "Monk", "max_hp": 120, "atk": 17, "def": 11, "spd": 105, "aggro": 70, "skills": ["Slash", "Smite"], "basic": "atk_warrior", "icon": "☯", "desc": "Petarung tangan kosong dengan stat seimbang dan lumayan cepat."},
    "SAMURAI": {"name": "Samurai", "max_hp": 130, "atk": 20, "def": 9, "spd": 100, "aggro": 80, "skills": ["Slash"], "basic": "atk_warrior", "icon": "⛩", "desc": "Pendekar pedang dengan daya rusak tinggi dan pertahanan lumayan."},
    "BERSERKER": {"name": "Berserker", "max_hp": 160, "atk": 24, "def": 4, "spd": 95, "aggro": 120, "skills": ["Slash"], "basic": "atk_warrior", "icon": "✖", "desc": "Petarung bar-bar. HP dan damage luar biasa, tapi pertahanan rapuh."},
    "ALCHEMIST": {"name": "Alchemist", "max_hp": 90, "atk": 12, "def": 10, "spd": 90, "aggro": 55, "skills": ["Fireball", "Poison Strike"], "basic": "atk_mage", "icon": "⚗", "desc": "Ahli racun dan bahan peledak. Serba bisa."},
    "ASSASSIN": {"name": "Assassin", "max_hp": 85, "atk": 26, "def": 5, "spd": 125, "aggro": 10, "skills": ["Backstab"], "basic": "atk_rogue", "icon": "♠", "desc": "Pembunuh berdarah dingin. Paling cepat bertindak dengan serangan kritikal."},
    "SORCERER": {"name": "Sorcerer", "max_hp": 75, "atk": 28, "def": 4, "spd": 85, "aggro": 25, "skills": ["Fireball"], "basic": "atk_mage", "icon": "✺", "desc": "Penyihir elemen murni. Damage tertinggi namun paling mudah mati."}
}

from models.hero import Hero
from database.skills_db import get_skill

def create_hero(role: str) -> Hero:
    data = HERO_ARCHETYPES[role]
    hero = Hero(role, data["name"], 1, data["max_hp"], data["atk"], data["def"], data["spd"], data["aggro"], role)
    hero.unlocked_skills = [get_skill(s_id) for s_id in data["skills"]]
    hero.equipped_skills = hero.unlocked_skills[:3]
    hero.basic_attack = get_skill(data["basic"])
    hero.name = f"{data['icon']} {hero.name}"
    return hero
