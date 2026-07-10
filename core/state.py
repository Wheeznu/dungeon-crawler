from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU = auto()
    TOWN_HUB = auto()
    SKILL_MENU = auto()
    INVENTORY = auto()
    COMBAT_INIT = auto()
    COMBAT_TICK = auto()
    COMBAT_PLAYER_TURN = auto()
    COMBAT_ANIMATION = auto()
    COMBAT_END = auto()
    CAMPFIRE = auto()
    GAME_OVER = auto()
