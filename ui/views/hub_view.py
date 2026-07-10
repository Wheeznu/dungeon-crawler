import curses
from database.classes_db import HERO_ARCHETYPES
from models.item import ItemType

def render_town_hub(stdscr, wm, party, highest_floor, gold, inventory_sys):
    stdscr.nodelay(False)
    selected = 0
    options = [
        "1. Masuk Dungeon (Mulai Pertarungan)", 
        "2. Manajemen Tim (Pilih 4 Anggota & Status)", 
        "3. Gudang Senjata (Equip Item)",
        "4. Toko Item (Jual Barang)",
        "5. Kedai Minum (Tavern - Rekrut Pahlawan)",
        "6. Save Game", 
        "7. Keluar (Quit)"
    ]
    
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
    
    max_y, max_x = stdscr.getmaxyx()
    title_h = 14
    win_title = curses.newwin(title_h, max_x, 0, 0)
    win_menu = curses.newwin(max_y - title_h, max_x // 2, title_h, 0)
    win_party = curses.newwin(max_y - title_h, max_x - (max_x // 2), title_h, max_x // 2)
    
    while True:
        win_title.clear()
        win_menu.clear()
        win_party.clear()
        
        try:
            # Draw Title Panel
            wm.draw_borders(win_title, " DUNGEON CRAWLER ")
            art_x = max(2, (max_x - 69) // 2)
            for i, line in enumerate(title_art):
                win_title.addstr(1+i, art_x, line, curses.color_pair(3))
                
            # Draw Menu Panel
            wm.draw_borders(win_menu, f" KOTA LINDUNG (Lantai: {highest_floor} | Gold: {gold} | Item: {len(inventory_sys.items)}) ")
            for i, opt in enumerate(options):
                prefix = "≫  " if i == selected else "   "
                win_menu.addstr(2+i, 3, f"{prefix}{opt}")
                
            # Draw Party Panel
            wm.draw_borders(win_party, " PARTY STATUS ")
            for i, h in enumerate(party[:4]):
                win_party.addstr(2+(i*3), 3, f"{h.name} ({h.role}) - Lv.{h.level}")
                wm.draw_progress_bar(win_party, 3+(i*3), 3, h.hp, h.max_hp, 20, "HP")
                
        except curses.error:
            pass
            
        win_title.refresh()
        win_menu.refresh()
        win_party.refresh()
        
        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                if bstate & curses.BUTTON1_CLICKED or bstate & curses.BUTTON1_PRESSED:
                    idx = wm.check_mouse_click(win_menu, my, mx, 2, 3, len(options), 1)
                    if idx != -1:
                        selected = idx
                        key = 10
            except curses.error: pass
        if key in [10, 13]:
            return selected

def render_team_management(stdscr, wm, roster):
    stdscr.nodelay(False)
    selected = 0
    swap_target = -1
    
    while True:
        wm.stdscr.clear()
        wm.stdscr.refresh()
        try:
            max_y, max_x = stdscr.getmaxyx()
            left_w = max_x // 3
            win_left = curses.newwin(max_y, left_w, 0, 0)
            win_right = curses.newwin(max_y, max_x - left_w, 0, left_w)
            
            wm.draw_borders(win_left, " MANAJEMEN TIM ")
            
            y_offset = 2
            win_left.addstr(y_offset, 2, "--- PARTY AKTIF (Maks 4) ---", curses.color_pair(3))
            y_offset += 1
            for i, h in enumerate(roster):
                if i == 4:
                    y_offset += 1
                    win_left.addstr(y_offset, 2, "--- CADANGAN ---", curses.color_pair(3))
                    y_offset += 1
                
                prefix = "≫ " if i == selected else "  "
                swap_str = " [PILIH]" if i == swap_target else ""
                color = curses.color_pair(2) if i == swap_target else 0
                win_left.addstr(y_offset, 2, f"{prefix}{h.name}{swap_str}", color)
                y_offset += 1
                
            wm.draw_borders(win_right, " DETAIL PAHLAWAN ")
            h = roster[selected]
            win_right.addstr(2, 4, f"Nama  : {h.name} ({h.role})", curses.color_pair(3))
            win_right.addstr(3, 4, f"Level : {h.level} (XP: {h.xp}/{h.xp_to_next})")
            win_right.addstr(5, 4, f"HP    : {h.hp}/{h.max_hp}")
            win_right.addstr(6, 4, f"ATK   : {h.atk}")
            win_right.addstr(7, 4, f"DEF   : {h.def_stat}")
            win_right.addstr(8, 4, f"SPD   : {h.spd}")
            
            SLOTS = [
                ("MAIN_WEAPON", "Senjata Utama"),
                ("SECONDARY_WEAPON", "Senjata Kedua"),
                ("HELM", "Helm         "),
                ("ARMOR", "Armor        "),
                ("GLOVES", "Sarung Tangan"),
                ("BOOTS", "Sepatu       "),
                ("RING", "Cincin       "),
                ("NECKLACE", "Kalung       ")
            ]
            
            for idx_slot, (s_key, s_name) in enumerate(SLOTS):
                eq_item = h.equipped.get(s_key)
                eq_name = eq_item.name if eq_item else "KOSONG"
                win_right.addstr(10 + idx_slot, 4, f"{s_name}: {eq_name}", curses.color_pair(4))
            
            win_right.addstr(max_y - 4, 4, "Instruksi:", curses.color_pair(3))
            if swap_target == -1:
                win_right.addstr(max_y - 3, 4, "- ENTER: Pilih hero untuk dipindah/swap")
            else:
                win_right.addstr(max_y - 3, 4, "- ENTER: Swap dengan hero terpilih [PILIH]")
            win_right.addstr(max_y - 2, 4, "- ESC/Q: Kembali")
            
            win_left.refresh()
            win_right.refresh()
        except curses.error: pass
        
        k = stdscr.getch()
        if k in [27, ord('q'), ord('Q')]:
            if swap_target != -1:
                swap_target = -1
            else:
                break
        elif k == curses.KEY_UP:
            selected = max(0, selected - 1)
        elif k == curses.KEY_DOWN:
            selected = min(len(roster) - 1, selected + 1)
        elif k in [10, 13]:
            if swap_target == -1:
                swap_target = selected
            else:
                if swap_target != selected:
                    # Lakukan swap posisi hero di roster
                    roster[swap_target], roster[selected] = roster[selected], roster[swap_target]
                    selected = swap_target  # Cursor ikuti hero ke posisi baru
                swap_target = -1

def render_equip_menu(stdscr, wm, roster, inventory_sys):
    stdscr.nodelay(False)
    sel_hero = 0
    sel_slot = 0
    sel_item = 0
    state = "HERO" # HERO, SLOT, ITEM
    
    SLOTS = [
        ("HELM", "Helm"),
        ("ARMOR", "Armor"),
        ("GLOVES", "Sarung Tangan"),
        ("BOOTS", "Sepatu"),
        ("RING", "Cincin"),
        ("NECKLACE", "Kalung"),
        ("MAIN_WEAPON", "Senjata Utama"),
        ("SECONDARY_WEAPON", "Senjata Kedua")
    ]
    
    while True:
        # Calculate equippables for current slot and hero
        equippables = []
        if roster:
            h = roster[sel_hero]
            slot_key = SLOTS[sel_slot][0]
            for it in inventory_sys.items:
                if it.item_type.name == slot_key:
                    if getattr(it, "usable_by", None) is None or h.role in it.usable_by:
                        equippables.append(it)
        
        if sel_item >= len(equippables): sel_item = max(0, len(equippables) - 1)
        
        wm.stdscr.clear()
        wm.stdscr.refresh()
        try:
            max_y, max_x = stdscr.getmaxyx()
            left_w = max_x // 4
            win_left = curses.newwin(max_y, left_w, 0, 0)
            win_right = curses.newwin(max_y, max_x - left_w, 0, left_w)
            
            wm.draw_borders(win_left, " PILIH HERO " if state == "HERO" else " HERO ")
            for i, h_ in enumerate(roster):
                prefix = "≫ " if (i == sel_hero and state == "HERO") else "  "
                win_left.addstr(2+i, 2, f"{prefix}{h_.name}")
                
            wm.draw_borders(win_right, " EQUIP / INVENTORY ")
            if roster:
                h = roster[sel_hero]
                win_right.addstr(2, 2, f"Target: {h.name} (Lv.{h.level}) | HP: {h.max_hp} | ATK: {h.atk} | DEF: {h.def_stat} | SPD: {h.spd}", curses.color_pair(3))
                
                # Draw slots
                for i, (s_key, s_name) in enumerate(SLOTS):
                    prefix = "≫ " if (i == sel_slot and state in ["SLOT", "ITEM"]) else "  "
                    eq_item = h.equipped.get(s_key)
                    eq_name = eq_item.name if eq_item else "KOSONG"
                    stats_str = ""
                    if eq_item:
                        stats_str = " | " + ", ".join([f"{k}: +{v}" for k,v in getattr(eq_item, 'stat_modifiers', {}).items()])
                    
                    color = curses.color_pair(4) if (i == sel_slot and state == "SLOT") else 0
                    win_right.addstr(4+i, 2, f"{prefix}{s_name:15}: {eq_name}{stats_str}", color)
                
                if state == "SLOT":
                    win_right.addstr(14, 2, "(Tekan ENTER untuk pilih item, 'u' untuk unequip)", curses.color_pair(1))
                elif state == "ITEM":
                    win_right.addstr(14, 2, "--- PILIH ITEM DARI INVENTORY ---", curses.color_pair(3))
                    if not equippables:
                        win_right.addstr(15, 2, "Tidak ada item yang cocok.")
                    else:
                        for i, it in enumerate(equippables):
                            if i > max_y - 19: break
                            prefix = "≫ " if i == sel_item else "  "
                            stats = " | ".join([f"{k}: +{v}" for k,v in getattr(it, 'stat_modifiers', {}).items()])
                            win_right.addstr(15+i, 2, f"{prefix}{it.name} ({stats})", curses.color_pair(2) if i == sel_item else 0)
                            
            win_right.addstr(max_y - 2, 2, "(ESC untuk kembali)")
            
            win_left.refresh()
            win_right.refresh()
        except curses.error: pass
        
        k = stdscr.getch()
        if k in [27, ord('q'), ord('Q')]:
            if state == "ITEM": state = "SLOT"
            elif state == "SLOT": state = "HERO"
            else: break
        elif k == curses.KEY_UP:
            if state == "HERO": sel_hero = max(0, sel_hero - 1)
            elif state == "SLOT": sel_slot = max(0, sel_slot - 1)
            elif state == "ITEM": sel_item = max(0, sel_item - 1)
        elif k == curses.KEY_DOWN:
            if state == "HERO": sel_hero = min(len(roster) - 1, sel_hero + 1)
            elif state == "SLOT": sel_slot = min(len(SLOTS) - 1, sel_slot + 1)
            elif state == "ITEM": sel_item = min(len(equippables) - 1, sel_item + 1)
        elif k in [ord('u'), ord('U')] and state == "SLOT":
            inventory_sys.unequip_hero(roster[sel_hero], SLOTS[sel_slot][0])
        elif k in [10, 13]:
            if state == "HERO" and roster:
                state = "SLOT"
            elif state == "SLOT":
                state = "ITEM"
                sel_item = 0
            elif state == "ITEM" and equippables:
                inventory_sys.equip_hero(roster[sel_hero], equippables[sel_item])
                state = "SLOT"

def render_tavern(stdscr, wm, roster, gold):
    stdscr.nodelay(False)
    selected = 0
    cost = 150
    in_party = [h.role for h in roster]
    available = [r for r in HERO_ARCHETYPES.keys() if r not in in_party]
    
    while True:
        wm.stdscr.clear()
        wm.stdscr.refresh()
        try:
            max_y, max_x = stdscr.getmaxyx()
            left_w = max_x // 3
            win_left = curses.newwin(max_y, left_w, 0, 0)
            win_right = curses.newwin(max_y, max_x - left_w, 0, left_w)
            
            wm.draw_borders(win_left, " KEDAI MINUM ")
            win_left.addstr(2, 2, f"Gold: {gold}G", curses.color_pair(3))
            win_left.addstr(3, 2, f"Biaya: {cost}G")
            
            if not available:
                win_left.addstr(5, 2, "Semua karakter direkrut!")
            else:
                for i, role in enumerate(available):
                    prefix = "≫ " if i == selected else "  "
                    win_left.addstr(6+i, 2, f"{prefix}{role}")
                    
            wm.draw_borders(win_right, " DETAIL KONTRAK ")
            if available:
                role = available[selected]
                arch = HERO_ARCHETYPES[role]
                win_right.addstr(2, 4, f"Class : {role}", curses.color_pair(4))
                
                desc = arch.get("desc", "Tidak ada deskripsi.")
                # We split description if it is too long
                if len(desc) > 30:
                    win_right.addstr(4, 4, f"Info  : {desc[:30]}")
                    win_right.addstr(5, 4, f"        {desc[30:]}")
                    o = 2
                else:
                    win_right.addstr(4, 4, f"Info  : {desc}")
                    o = 1
                
                win_right.addstr(4+o, 4, f"HP    : {arch['max_hp']}")
                win_right.addstr(5+o, 4, f"ATK   : {arch['atk']}")
                win_right.addstr(6+o, 4, f"DEF   : {arch['def']}")
                win_right.addstr(7+o, 4, f"SPD   : {arch['spd']}")
                win_right.addstr(10+o, 4, "(Tekan ENTER untuk merekrut pahlawan ini)")
                
            win_left.refresh()
            win_right.refresh()
        except curses.error: pass
        
        k = stdscr.getch()
        if k in [27, ord('q'), ord('Q')]:
            return None
        elif k == curses.KEY_UP and available:
            selected = max(0, selected - 1)
        elif k == curses.KEY_DOWN and available:
            selected = min(len(available) - 1, selected + 1)
        elif k in [10, 13] and available:
            if gold >= cost:
                return available[selected]
            else:
                try: 
                    win_right.addstr(12, 4, "GOLD TIDAK CUKUP!", curses.color_pair(1))
                    win_right.refresh()
                except: pass
                curses.napms(1000)

def render_level_selection(stdscr, wm, highest_floor):
    stdscr.nodelay(False)
    selected_floor = highest_floor
    
    while True:
        wm.stdscr.clear()
        wm.stdscr.refresh()
        try:
            max_y, max_x = stdscr.getmaxyx()
            box_w = 50
            box_h = 13
            start_y = (max_y - box_h) // 2
            start_x = (max_x - box_w) // 2
            
            win = curses.newwin(box_h, box_w, start_y, start_x)
            wm.draw_borders(win, " PILIH LANTAI DUNGEON ")
            
            header = f"Lantai Tertinggi Dicapai: {highest_floor}"
            win.addstr(2, (box_w - len(header)) // 2, header, curses.color_pair(3))
            
            # Draw a nice selector
            selector_text = f"◀◀  LANTAI {selected_floor:02d}  ▶▶"
            win.addstr(5, (box_w - len(selector_text)) // 2, selector_text, curses.color_pair(4) | curses.A_BOLD)
            
            # Floor info
            is_boss = (selected_floor % 10 == 0)
            if is_boss:
                info_text = "⚠ WARNING: BOSS FLOOR ⚠"
                win.addstr(7, (box_w - len(info_text)) // 2, info_text, curses.color_pair(1) | curses.A_BLINK)
            else:
                info_text = "Lantai Standar - Hati-hati!"
                win.addstr(7, (box_w - len(info_text)) // 2, info_text, curses.color_pair(2))
            
            footer1 = "[ENTER] Mulai   [ESC] Batal"
            footer2 = "(Panah KIRI/KANAN untuk mengganti)"
            win.addstr(9, (box_w - len(footer1)) // 2, footer1)
            win.addstr(10, (box_w - len(footer2)) // 2, footer2, curses.color_pair(8) if curses.COLORS >= 8 else 0)
            
            win.refresh()
        except curses.error: pass
        
        key = stdscr.getch()
        
        if key in [27, ord('q'), ord('Q')]:
            return None
        elif key == curses.KEY_LEFT:
            selected_floor = max(1, selected_floor - 1)
        elif key == curses.KEY_RIGHT:
            selected_floor = min(highest_floor, selected_floor + 1)
        if key in [10, 13]:
            return selected_floor

def render_shop_menu(stdscr, wm, gold, inventory_sys):
    stdscr.nodelay(False)
    selected = 0
    message = ""
    
    while True:
        items = inventory_sys.items
        if selected >= len(items): selected = max(0, len(items) - 1)
        
        wm.stdscr.clear()
        wm.stdscr.refresh()
        try:
            max_y, max_x = stdscr.getmaxyx()
            left_w = max_x // 3
            win_left = curses.newwin(max_y, left_w, 0, 0)
            win_right = curses.newwin(max_y, max_x - left_w, 0, left_w)
            
            wm.draw_borders(win_left, " TOKO BARANG ")
            win_left.addstr(2, 2, f"Gold Anda: {gold}G", curses.color_pair(3))
            
            if message:
                win_left.addstr(4, 2, message, curses.color_pair(4))
                message = ""
                
            win_left.addstr(max_y - 2, 2, "(ESC untuk kembali)")
            
            wm.draw_borders(win_right, " DAFTAR BARANG (JUAL) ")
            if not items:
                win_right.addstr(2, 2, "Inventory kosong. Tidak ada yang bisa dijual.")
            else:
                for i, it in enumerate(items):
                    prefix = "≫ " if i == selected else "  "
                    # Only show 15 items to avoid overflow, adjust later if scrolling needed
                    if i < 15:
                        win_right.addstr(2+i, 2, f"{prefix}{it.name} ({it.rarity.name}) - Harga Jual: {it.value}G", curses.color_pair(3))
                
                if items:
                    win_right.addstr(max_y - 2, 2, "(Tekan ENTER untuk menjual item yang dipilih)")
                    
            win_left.refresh()
            win_right.refresh()
        except curses.error: pass
        
        k = stdscr.getch()
        if k in [27, ord('q'), ord('Q')]:
            return gold
        elif k == curses.KEY_UP:
            selected = max(0, selected - 1)
        elif k == curses.KEY_DOWN:
            selected = min(len(items) - 1, selected + 1)
        elif k in [10, 13] and items:
            item_to_sell = items[selected]
            gold += item_to_sell.value
            inventory_sys.items.remove(item_to_sell)
            message = f"Terjual: {item_to_sell.name} (+{item_to_sell.value}G)"

