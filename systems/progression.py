def calculate_xp_required(level: int) -> int:
    return int(level * 100 * 1.5)

def check_level_up(hero):
    leveled_up = False
    while hero.xp >= hero.xp_to_next:
        hero.level_up()
        leveled_up = True
    return leveled_up
