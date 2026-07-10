import curses

class WindowManager:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.start_color()
        curses.use_default_colors()
        
        curses.init_pair(1, curses.COLOR_RED, -1)     # HP / Damage
        curses.init_pair(2, curses.COLOR_CYAN, -1)    # MP / Magic
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Legendary / Gold
        curses.init_pair(4, curses.COLOR_GREEN, -1)   # Heal / Uncommon
        curses.init_pair(5, curses.COLOR_MAGENTA, -1) # Epic / Status
        curses.init_pair(6, curses.COLOR_BLUE, -1)    # Rare
        
        self.stdscr = stdscr
        max_y, max_x = stdscr.getmaxyx()
        
        # Restore full width/height but with better proportional distribution
        self.max_x = max_x
        self.max_y = max_y
        
        if self.max_y < 15:
            raise Exception(f"Terminal height {self.max_y} is too small! Please expand your terminal (minimum 15 lines).")
            
        enemy_h = max(5, int(self.max_y * 0.3))
        hero_h = max(13, int(self.max_y * 0.35))
        log_h = self.max_y - enemy_h - hero_h
        
        self.win_enemies = curses.newwin(enemy_h, self.max_x, 0, 0)
        self.win_log = curses.newwin(log_h, self.max_x, enemy_h, 0)
        self.win_heroes = curses.newwin(hero_h, self.max_x, enemy_h + log_h, 0)
        
    def draw_borders(self, win, title=""):
        win.clear()
        win.box()
        if title:
            win.addstr(0, 2, f" {title} ")
            
    def draw_progress_bar(self, win, y, x, current, maximum, length=10, prefix="HP"):
        ratio = max(0.0, min(1.0, current / max(maximum, 1)))
        filled = int(ratio * length)
        empty = length - filled
        
        color = curses.color_pair(4)
        if ratio <= 0.25: color = curses.color_pair(1)
        elif ratio <= 0.5: color = curses.color_pair(3)
            
        bar = "█" * filled + "░" * empty
        text = f"{prefix}: [{bar}] {current:03d}/{maximum:03d}"
        
        try:
            win.addstr(y, x, text, color)
        except curses.error:
            pass
            
    def refresh_all(self):
        self.win_enemies.noutrefresh()
        self.win_log.noutrefresh()
        self.win_heroes.noutrefresh()
        curses.doupdate()

    def draw_loading_screen(self, message="LOADING..."):
        self.stdscr.clear()
        try:
            max_y, max_x = self.stdscr.getmaxyx()
            self.stdscr.addstr(max_y // 2, max(0, (max_x - len(message)) // 2), message, curses.color_pair(3))
        except curses.error:
            pass
        self.stdscr.refresh()

    def check_mouse_click(self, win, event_y, event_x, start_y, start_x, item_count, line_height=1):
        win_y, win_x = win.getbegyx()
        
        rel_y = event_y - win_y
        rel_x = event_x - win_x
        
        if rel_y >= start_y and rel_y < start_y + (item_count * line_height):
            if rel_x >= start_x:
                idx = (rel_y - start_y) // line_height
                return idx
        return -1
