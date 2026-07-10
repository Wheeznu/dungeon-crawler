import curses
from core.save_manager import check_save_slots, get_save_info
from systems.translation import translate
from systems.config import config

def render_start_menu(stdscr, wm):
    stdscr.nodelay(False)
    selected = 0
    
    title_art = [
        "  ██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗",
        "  ██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║",
        "  ██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║",
        "  ██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║",
        "  ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║",
        "  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝",
        "    ██████╗██████╗  █████╗ ██╗    ██╗██╗     ███████╗██████╗     ",
        "   ██╔════╝██╔══██╗██╔══██╗██║    ██║██║     ██╔════╝██╔══██╗    ",
        "   ██║     ██████╔╝███████║██║ █╗ ██║██║     █████╗  ██████╔╝    ",
        "   ██║     ██╔══██╗██╔══██║██║███╗██║██║     ██╔══╝  ██╔══██╗    ",
        "   ╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗███████╗██║  ██║    ",
        "    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝  ╚═╝    "
    ]
    
    while True:
        has_saves = check_save_slots()
        options = []
        if has_saves:
            options.append("Continue")
        options.append("New Game")
        options.extend(["Options", "Quit"])
        
        # Ensure selected is within bounds (in case Continue was removed/added)
        selected = min(selected, len(options) - 1)
        
        wm.stdscr.clear()
        try:
            max_y, max_x = stdscr.getmaxyx()
            
            # Draw Title
            art_x = max(2, (max_x - 69) // 2)
            art_y = max(2, (max_y - 20) // 2)
            
            for i, line in enumerate(title_art):
                wm.stdscr.addstr(art_y + i, art_x, line, curses.color_pair(3))
                
            menu_y = art_y + 14
            for i, opt in enumerate(options):
                prefix = "≫ " if i == selected else "  "
                wm.stdscr.addstr(menu_y + i, art_x + 25, f"{prefix}{opt}", curses.color_pair(4 if i == selected else 0))
                
        except curses.error:
            pass
            
        wm.stdscr.refresh()
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                if bstate & curses.BUTTON1_CLICKED or bstate & curses.BUTTON1_PRESSED:
                    idx = wm.check_mouse_click(wm.stdscr, my, mx, menu_y, art_x + 25, len(options), 1)
                    if idx != -1:
                        selected = idx
                        key = 10
            except curses.error: pass
        if key in [10, 13]:
            choice = options[selected]
            if choice == "New Game":
                # Select slot for new game
                slot = render_save_slot_menu(stdscr, wm, translate("new_slot_title"))
                if slot: return ("NEW_GAME", slot)
            elif choice == "Continue":
                slot = render_save_slot_menu(stdscr, wm, translate("load_slot_title"))
                if slot: return ("LOAD_GAME", slot)
            elif choice == "Options":
                render_options_menu(stdscr, wm)
            elif choice == "Quit":
                return ("QUIT", None)

def render_save_slot_menu(stdscr, wm, title):
    selected = 0
    while True:
        wm.stdscr.clear()
        wm.stdscr.refresh()
        try:
            max_y, max_x = stdscr.getmaxyx()
            box_w = 60
            box_h = 10
            start_y = (max_y - box_h) // 2
            start_x = (max_x - box_w) // 2
            
            win = curses.newwin(box_h, box_w, start_y, start_x)
            wm.draw_borders(win, f" {title} ")
            
            for i in range(1, 4):
                info = get_save_info(i)
                prefix = "≫ " if (i-1) == selected else "  "
                if info["exists"]:
                    text = f"Slot {i}: {'Lantai' if config.get('language', 'ID') == 'ID' else 'Floor'} {info['floor']} | Gold: {info['gold']} | Hero: {info['heroes']}"
                else:
                    text = f"Slot {i}: {translate('save_slot_empty')}"
                win.addstr(2 + (i-1)*2, 4, f"{prefix}{text}")
                
            win.addstr(8, 4, translate("back_esc"))
            win.refresh()
        except curses.error:
            pass
            
        key = stdscr.getch()
        if key in [27, ord('q'), ord('Q')]:
            return None
        elif key == curses.KEY_UP:
            selected = (selected - 1) % 3
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % 3
        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                if bstate & curses.BUTTON1_CLICKED or bstate & curses.BUTTON1_PRESSED:
                    idx = wm.check_mouse_click(win, my, mx, 2, 4, 3, 2)
                    if idx != -1:
                        selected = idx
                        key = 10
            except curses.error: pass
        if key in [10, 13]:
            return selected + 1

def render_options_menu(stdscr, wm):
    from systems.config import config, save_settings
    selected = 0
    
    while True:
        options = [
            f"Difficulty: {config['difficulty']}",
            f"Auto-Save: {'ON' if config['auto_save'] else 'OFF'}",
            f"Visual FX: {'ON' if config['visual_fx'] else 'OFF'}",
            f"Combat Log Lines: {config['log_lines']}",
            f"Language: {config['language']}",
            translate("options_back")
        ]
        
        wm.stdscr.clear()
        wm.stdscr.refresh()
        try:
            max_y, max_x = stdscr.getmaxyx()
            box_w = 50
            box_h = 15
            start_y = (max_y - box_h) // 2
            start_x = (max_x - box_w) // 2
            
            win = curses.newwin(box_h, box_w, start_y, start_x)
            wm.draw_borders(win, translate("options_title"))
            
            for i, opt in enumerate(options):
                prefix = "≫ " if i == selected else "  "
                win.addstr(2 + i*2, 4, f"{prefix}{opt}")
                
            win.refresh()
        except curses.error:
            pass
            
        key = stdscr.getch()
        if key in [27, ord('q'), ord('Q')]:
            save_settings()
            return
        elif key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key == curses.KEY_LEFT or key == curses.KEY_RIGHT or key in [10, 13]:
            if selected == 0:
                diffs = ["EASY", "NORMAL", "HARD"]
                idx = diffs.index(config["difficulty"])
                if key == curses.KEY_LEFT:
                    idx = (idx - 1) % len(diffs)
                else:
                    idx = (idx + 1) % len(diffs)
                config["difficulty"] = diffs[idx]
            elif selected == 1:
                config["auto_save"] = not config["auto_save"]
            elif selected == 2:
                config["visual_fx"] = not config["visual_fx"]
            elif selected == 3:
                lines = [8, 12, 16]
                idx = lines.index(config["log_lines"])
                if key == curses.KEY_LEFT:
                    idx = (idx - 1) % len(lines)
                else:
                    idx = (idx + 1) % len(lines)
                config["log_lines"] = lines[idx]
            elif selected == 4:
                langs = ["ID", "EN"]
                idx = langs.index(config["language"])
                if key == curses.KEY_LEFT:
                    idx = (idx - 1) % len(langs)
                else:
                    idx = (idx + 1) % len(langs)
                config["language"] = langs[idx]
            elif selected == 5:
                if key in [10, 13]:
                    save_settings()
                    return
        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                if bstate & curses.BUTTON1_CLICKED or bstate & curses.BUTTON1_PRESSED:
                    idx = wm.check_mouse_click(win, my, mx, 2, 4, len(options), 2)
                    if idx != -1:
                        if selected == idx:
                            key = 10
                            curses.ungetch(key)
                        else:
                            selected = idx
            except curses.error: pass

