import curses
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.logger import log
from core.state import GameState
from database.classes_db import HERO_ARCHETYPES, create_hero
from database.enemies_db import get_waves_for_floor
from systems.combat_engine import CombatEngine
from systems.loot_system import generate_loot
from systems.inventory_system import InventorySystem
from ui.window_manager import WindowManager
from ui.animation import AnimationEngine
from models.skill import TargetType
from models.item import Rarity
from database.items_db import get_base_item
from ui.views.hub_view import render_town_hub, render_team_management, render_tavern, render_level_selection, render_equip_menu, render_shop_menu
from ui.views.start_menu import render_start_menu
from core.save_manager import save_game, load_game

def player_turn(stdscr, wm, actor, heroes, enemies, engine):
    stdscr.nodelay(False)
    
    actions = [actor.basic_attack] + actor.equipped_skills
    sel_action = 0
    
    while True:
        while True:
            try:
                wm.win_heroes.clear()
                wm.draw_borders(wm.win_heroes, " HERO INFO & ACTIONS ")
                max_y, max_x = wm.win_heroes.getmaxyx()
                mid_x = max_x // 2
                
                # LEFT COLUMN: Action Menu
                menu_start_y = 2
                wm.win_heroes.addstr(menu_start_y, 2, f"GILIRAN: {actor.name} (HP: {actor.hp}/{actor.max_hp})", curses.color_pair(3))
                wm.win_heroes.addstr(menu_start_y+2, 2, "Pilih Aksi (Atas/Bawah, Enter):")
                for i, action in enumerate(actions):
                    prefix = "[x] " if i == sel_action else "[ ] "
                    wm.win_heroes.addstr(menu_start_y+3+i, 4, f"{prefix}{action.name} (Cost: {action.action_cost} AP)")
                    
                desc = actions[sel_action].description
                wm.win_heroes.addstr(max_y - 2, 2, f"INFO: {desc[:mid_x-4]}", curses.color_pair(3))
                
                # RIGHT COLUMN: Party HP
                wm.win_heroes.addstr(2, mid_x, "STATUS PARTY:", curses.color_pair(4))
                for i, h in enumerate(heroes):
                    hp_str = f"HP: {h.hp}/{h.max_hp}"
                    wm.win_heroes.addstr(4+i, mid_x, f"{h.name[:12]:12} | {hp_str:15}")
                    
            except curses.error:
                pass
                
            wm.win_heroes.refresh()
            
            key = stdscr.getch()
            if key == curses.KEY_UP:
                sel_action = (sel_action - 1) % len(actions)
            elif key == curses.KEY_DOWN:
                sel_action = (sel_action + 1) % len(actions)
            elif key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    if bstate & curses.BUTTON1_CLICKED or bstate & curses.BUTTON1_PRESSED:
                        idx = wm.check_mouse_click(wm.win_heroes, my, mx, menu_start_y+3, 4, len(actions), 1)
                        if idx != -1:
                            sel_action = idx
                            key = 10
                except curses.error: pass
            if key in [ord('a'), ord('A')]:
                return True
            if key in [10, 13]:
                break
                
        skill = actions[sel_action]
        
        alive_enemies = [e for e in enemies if not e.is_dead]
        alive_heroes = [h for h in heroes if not h.is_dead]
        
        if not alive_enemies:
            return
            
        if skill.target_type == TargetType.SELF:
            target = actor
            break
        else:
            if skill.target_type in [TargetType.SINGLE_ENEMY, TargetType.ALL_ENEMIES, TargetType.BLAST]:
                valid = alive_enemies
                is_enemy = True
            else:
                valid = alive_heroes
                is_enemy = False
                
            if not valid:
                target = actor
                break
            else:
                sel_target = 0
                canceled = False
                while True:
                    win_t = wm.win_enemies if is_enemy else wm.win_heroes
                    win_t.clear()
                    wm.draw_borders(win_t, " PILIH TARGET (ESC: Batal) ")
                    
                    try:
                        for i, ent in enumerate(valid):
                            prefix = "   "
                            if skill.target_type in [TargetType.ALL_ENEMIES, TargetType.ALL_ALLIES]:
                                prefix = "≫  "
                            elif skill.target_type == TargetType.BLAST:
                                if i == sel_target: prefix = "≫  "
                                elif i == sel_target - 1 or i == sel_target + 1: prefix = ">  "
                            else:
                                if i == sel_target: prefix = "≫  "
                                
                            win_t.addstr(1+i, 2, f"{prefix}{ent.name}")
                            wm.draw_progress_bar(win_t, 1+i, 25, ent.hp, ent.max_hp, 10, "HP")
                    except curses.error:
                        pass
                        
                    win_t.refresh()
                    
                    key = stdscr.getch()
                    if key in [27, ord('q'), ord('Q')]:
                        canceled = True
                        break
                    
                    if skill.target_type in [TargetType.ALL_ENEMIES, TargetType.ALL_ALLIES]:
                        if key in [10, 13]: break
                    else:
                        if key == curses.KEY_UP:
                            sel_target = (sel_target - 1) % len(valid)
                        elif key == curses.KEY_DOWN:
                            sel_target = (sel_target + 1) % len(valid)
                        elif key == curses.KEY_MOUSE:
                            try:
                                _, mx, my, _, bstate = curses.getmouse()
                                if bstate & curses.BUTTON1_CLICKED or bstate & curses.BUTTON1_PRESSED:
                                    idx = wm.check_mouse_click(win_t, my, mx, 1, 2, len(valid), 1)
                                    if idx != -1:
                                        sel_target = idx
                                        key = 10
                            except curses.error: pass
                        if key in [10, 13]:
                            break
                            
                if canceled:
                    continue # loop back to skill selection
                    
                target = valid[sel_target] if skill.target_type != TargetType.ALL_ENEMIES else valid[0]
                break
                
    engine.execute_action(actor, skill, target)
    stdscr.nodelay(True)

def main(stdscr):
    from systems.config import load_settings, config
    load_settings()
    curses.curs_set(0)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    wm = WindowManager(stdscr)
    anim = AnimationEngine()
    
    while True:
        action, slot = render_start_menu(stdscr, wm)
        if action == "QUIT":
            break
            
        inventory_sys = InventorySystem()
        if action == "NEW_GAME":
            wm.draw_loading_screen("Memulai Game Baru...")
            roster = [create_hero("WARRIOR"), create_hero("MAGE")]
            highest_floor = 1
            gold = 200
            active_slot = slot
            unsaved_progress = True
        elif action == "LOAD_GAME":
            wm.draw_loading_screen(f"Memuat Save Data {slot}...")
            data = load_game(slot)
            roster = []
            if data and "roster" in data:
                for h_data in data["roster"]:
                    h = create_hero(h_data.get("role", "WARRIOR"))
                    h.level = h_data.get("level", 1)
                    h.xp = h_data.get("xp", 0)
                    h.max_hp = h_data.get("max_hp", h.max_hp)
                    h.hp = h_data.get("hp", h.max_hp)
                    h.atk = h_data.get("atk", h.atk)
                    h.def_stat = h_data.get("def_stat", h.def_stat)
                    h.spd = h_data.get("spd", h.spd)
                    
                    # Load equipment and apply stats correctly
                    equipped = h_data.get("equipped", {})
                    for slot_name, eq_info in equipped.items():
                        if eq_info:
                            try:
                                item = get_base_item(eq_info["base_id"], Rarity(eq_info["rarity"]), eq_info["floor_level"])
                                if item:
                                    h.equipped[slot_name] = item
                            except Exception:
                                pass
                    roster.append(h)
                for i_data in data.get("inventory", []):
                    try:
                        item = get_base_item(i_data["base_id"], Rarity(i_data["rarity"]), i_data["floor_level"])
                        if item: inventory_sys.add_item(item)
                    except: pass
                highest_floor = data.get("current_floor", 1)
                gold = data.get("gold", 0)
            else:
                roster = [create_hero("WARRIOR"), create_hero("MAGE")]
                highest_floor = 1
                gold = 200
            active_slot = slot
            unsaved_progress = False

        state = GameState.TOWN_HUB
        active_floor = 1
        
        while state != "RETURN_TO_MAIN":
            if state == GameState.TOWN_HUB:
                choice = render_town_hub(stdscr, wm, roster, highest_floor, gold, inventory_sys)
                if choice == 0:
                    if not roster: continue
                    sel = render_level_selection(stdscr, wm, highest_floor)
                    if sel is not None:
                        active_floor = sel
                        wm.draw_loading_screen(f"Memasuki Lantai {active_floor}...")
                        state = GameState.COMBAT_INIT
                elif choice == 1:
                    render_team_management(stdscr, wm, roster)
                    # changing equip could be unsaved progress, but we'll assume it is for now
                    unsaved_progress = True
                elif choice == 2:
                    render_equip_menu(stdscr, wm, roster, inventory_sys)
                    unsaved_progress = True
                elif choice == 3:
                    gold = render_shop_menu(stdscr, wm, gold, inventory_sys)
                    unsaved_progress = True
                elif choice == 4:
                    new_hero_role = render_tavern(stdscr, wm, roster, gold)
                    if new_hero_role:
                        gold -= 150
                        roster.append(create_hero(new_hero_role))
                        unsaved_progress = True
                elif choice == 5:
                    from ui.views.start_menu import render_save_slot_menu
                    sel_slot = render_save_slot_menu(stdscr, wm, "Pilih Slot untuk Menyimpan")
                    if sel_slot:
                        save_game(roster, gold, highest_floor, inventory_sys.items, sel_slot)
                        active_slot = sel_slot
                        unsaved_progress = False
                        stdscr.nodelay(False)
                        wm.stdscr.clear()
                        try: wm.stdscr.addstr(5, 5, f"Game berhasil disimpan di Slot {active_slot}! (Tekan tombol apapun)", curses.color_pair(4))
                        except curses.error: pass
                        wm.stdscr.refresh()
                        stdscr.getch()
                elif choice == 6:
                    if unsaved_progress:
                        wm.stdscr.clear()
                        wm.stdscr.refresh()
                        try:
                            max_y, max_x = wm.stdscr.getmaxyx()
                            box_w = 46
                            box_h = 7
                            start_y = (max_y - box_h) // 2
                            start_x = (max_x - box_w) // 2
                            win = curses.newwin(box_h, box_w, start_y, start_x)
                            wm.draw_borders(win, " WARNING ")
                            win.addstr(2, 2, "ADA PROGRESS YANG BELUM DISAVE!", curses.color_pair(1) | curses.A_BOLD)
                            win.addstr(4, 2, "YAKIN INGIN KELUAR KE MAIN MENU? (Y/N)")
                            win.refresh()
                        except curses.error: pass
                        confirmed = False
                        while True:
                            k = stdscr.getch()
                            if k in [ord('y'), ord('Y')]:
                                confirmed = True
                                break
                            elif k in [ord('n'), ord('N')]:
                                break
                        if confirmed:
                            state = "RETURN_TO_MAIN"
                    else:
                        state = "RETURN_TO_MAIN"
                        
            elif state == GameState.COMBAT_INIT:
                party = roster[:4]
                for h in party:
                    if h.is_dead: h.heal(h.max_hp // 10)
                    else: h.heal(h.max_hp)
                    h.action_points = 0
                    
                waves = get_waves_for_floor(active_floor)
                max_waves = len(waves)
                current_wave_idx = 0
                
                floor_cleared = False
                combat_lost = False
                auto_battle_enabled = False
                total_gold_gained = 0
                total_loot = []
                
                stdscr.nodelay(True)
                wm.stdscr.clear()
                wm.stdscr.refresh()
                
                while current_wave_idx < max_waves and not combat_lost:
                    enemies = waves[current_wave_idx]
                    engine = CombatEngine(party, enemies, anim.queue)
                    
                    # Reset hero AP for new wave
                    for h in party:
                        if not h.is_dead:
                            h.action_points = 0
                            
                    combat_running = True
                    status = "ONGOING"
                    
                    while combat_running:
                        # Listen for toggle during animation frames
                        stdscr.nodelay(True)
                        k = stdscr.getch()
                        stdscr.nodelay(False)
                        if k in [ord('a'), ord('A')]:
                            auto_battle_enabled = not auto_battle_enabled
                            
                        actor = engine.tick()
                        if actor:
                            if actor in party:
                                if auto_battle_enabled:
                                    engine.run_auto_battle(actor)
                                else:
                                    toggled = player_turn(stdscr, wm, actor, party, enemies, engine)
                                    if toggled:
                                        auto_battle_enabled = True
                                        engine.run_auto_battle(actor)
                            else:
                                engine.run_ai_turn(actor)
                                
                            status = engine.check_victory()
                            if status != "ONGOING":
                                combat_running = False
                                
                        anim.process_tick()
                        
                        wm.win_enemies.clear()
                        wm.draw_borders(wm.win_enemies, f" ENEMIES (Lantai {active_floor} - Wave {current_wave_idx+1}/{max_waves}) ")
                        try:
                            for i, e in enumerate(enemies):
                                wm.win_enemies.addstr(1+i, 2, f"{e.name}")
                                wm.draw_progress_bar(wm.win_enemies, 1+i, 25, e.hp, e.max_hp, 10, "HP")
                        except curses.error: pass
                            
                        wm.win_heroes.clear()
                        title_heroes = f" HEROES [AUTO: {'ON' if auto_battle_enabled else 'OFF'} (Tekan A)] "
                        wm.draw_borders(wm.win_heroes, title_heroes)
                        try:
                            for i, h in enumerate(party):
                                wm.win_heroes.addstr(1+i, 2, f"{h.name} ({h.role})")
                                wm.draw_progress_bar(wm.win_heroes, 1+i, 28, h.hp, h.max_hp, 15, "HP")
                                wm.win_heroes.addstr(1+i, 62, f"AP: {h.action_points}")
                        except curses.error: pass
                            
                        wm.win_log.clear()
                        wm.draw_borders(wm.win_log, " ACTION TIMELINE / LOG ")
                        
                        all_entities = party + enemies
                        alive_entities = [ent for ent in all_entities if not ent.is_dead]
                        alive_entities.sort(key=lambda x: x.action_points, reverse=True)
                        try:
                            max_y, max_x = wm.win_log.getmaxyx()
                            if max_x > 45:
                                wm.win_log.addstr(1, 2, "=== ANTRIAN GILIRAN ===", curses.color_pair(3))
                                for i, ent in enumerate(alive_entities[:5]):
                                    color = curses.color_pair(2) if ent in party else curses.color_pair(1)
                                    fill = min(10, int((ent.action_points / 1000) * 10))
                                    bar = "█" * fill + "░" * (10 - fill)
                                    wm.win_log.addstr(2+i, 2, f"[{bar}] {ent.name[:18]}", color)
                                    
                                wm.win_log.addstr(8, 2, "=== COMBAT LOG ===", curses.color_pair(4))
                                for i, log_text in enumerate(anim.combat_log[-config['log_lines']:]):
                                    wm.win_log.addstr(9+i, 2, log_text[:max_x-4])
                        except curses.error: pass
                        
                        if config["visual_fx"]:
                            for t in anim.floating_texts:
                                try:
                                    wm.win_log.addstr(t["y"], max_x - 15, t["text"], curses.color_pair(t["color"]))
                                except curses.error:
                                    pass
                                
                        wm.refresh_all()
                        if config['visual_fx']:
                            time.sleep(0.05)
                        
                    # End of a wave
                    stdscr.nodelay(False)
                    wm.stdscr.clear()
                    
                    if status == "VICTORY":
                        is_boss = (active_floor % 10 == 0)
                        wave_gold = active_floor * 15
                        gold += wave_gold
                        total_gold_gained += wave_gold
                        
                        wave_loot = generate_loot(active_floor, party, is_boss)
                        loot_msg = "Tidak ada item drop."
                        if wave_loot:
                            inventory_sys.add_item(wave_loot)
                            total_loot.append(wave_loot)
                            loot_msg = f"Item Drop: {wave_loot.name} ({wave_loot.rarity.name})"
                            
                        for h in party:
                            if not h.is_dead:
                                h.xp += active_floor * 60
                                
                        current_wave_idx += 1
                        if current_wave_idx == max_waves:
                            floor_cleared = True
                        else:
                            wm.stdscr.clear()
                            try:
                                max_y, max_x = stdscr.getmaxyx()
                                center_y = max_y // 2
                                
                                title = f"=== WAVE {current_wave_idx} CLEARED! ==="
                                wm.stdscr.addstr(center_y - 3, max(0, (max_x - len(title)) // 2), title, curses.color_pair(3) | curses.A_BOLD)
                                
                                msg1 = f"* Mendapat {wave_gold} Gold."
                                wm.stdscr.addstr(center_y - 1, max(0, (max_x - len(msg1)) // 2), msg1, curses.color_pair(3))
                                
                                msg2 = f"- {loot_msg}"
                                wm.stdscr.addstr(center_y, max(0, (max_x - len(msg2)) // 2), msg2)
                                
                                prompt = "(Tekan tombol apapun untuk lanjut...)"
                                wm.stdscr.addstr(center_y + 3, max(0, (max_x - len(prompt)) // 2), prompt, curses.color_pair(4))
                                
                                wm.stdscr.refresh()
                            except curses.error: pass
                            stdscr.getch()
                            stdscr.nodelay(True)
                    else:
                        combat_lost = True
                
                # End of entire floor
                stdscr.nodelay(False)
                wm.stdscr.clear()
                
                if floor_cleared:
                    from systems.progression import check_level_up
                    for h in party:
                        if not h.is_dead:
                            check_level_up(h)
                            
                    if active_floor == highest_floor:
                        highest_floor += 1
                        
                    art = [
                        "██╗   ██╗██╗ ██████╗████████╗██████╗ ██████╗ ██╗   ██╗",
                        "██║   ██║██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚██╗ ██╔╝",
                        "██║   ██║██║██║        ██║   ██║  ██║██████╔╝ ╚████╔╝ ",
                        "╚██╗ ██╔╝██║██║        ██║   ██║  ██║██╔══██╗  ╚██╔╝  ",
                        " ╚████╔╝ ██║╚██████╗   ██║   ██████╔╝██║  ██║   ██║   ",
                        "  ╚═══╝  ╚═╝ ╚═════╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   "
                    ]
                    try:
                        max_y, max_x = stdscr.getmaxyx()
                        center_y = max_y // 2
                        
                        art_start_y = max(0, center_y - 8)
                        art_x = max(0, (max_x - 56) // 2)
                        for i, line in enumerate(art):
                            wm.stdscr.addstr(art_start_y+i, art_x, line, curses.color_pair(3) | curses.A_BOLD)
                            
                        msg1 = f"* Total Gold Diperoleh: {total_gold_gained}"
                        wm.stdscr.addstr(center_y + 1, max(0, (max_x - len(msg1)) // 2), msg1, curses.color_pair(3))
                        
                        loot_summary = ", ".join([l.name for l in total_loot]) if total_loot else "Tidak Ada"
                        if len(loot_summary) > 60: loot_summary = loot_summary[:57] + "..."
                        msg2 = f"- Item Drop ({len(total_loot)}): {loot_summary}"
                        wm.stdscr.addstr(center_y + 2, max(0, (max_x - len(msg2)) // 2), msg2)
                        
                        msg3 = "* Semua hero mendapatkan XP!"
                        wm.stdscr.addstr(center_y + 4, max(0, (max_x - len(msg3)) // 2), msg3, curses.color_pair(4))
                        
                        prompt = "(Tekan tombol apapun untuk kembali ke Kota...)"
                        wm.stdscr.addstr(center_y + 6, max(0, (max_x - len(prompt)) // 2), prompt, curses.color_pair(1))
                        
                        wm.stdscr.refresh()
                    except curses.error: pass
                    stdscr.getch()
                else:
                    try:
                        max_y, max_x = stdscr.getmaxyx()
                        center_y = max_y // 2
                        
                        title = "=== GAME OVER ==="
                        wm.stdscr.addstr(center_y - 2, max(0, (max_x - len(title)) // 2), title, curses.color_pair(1) | curses.A_BOLD)
                        
                        msg1 = "X KALAH! Party kamu terbunuh..."
                        wm.stdscr.addstr(center_y, max(0, (max_x - len(msg1)) // 2), msg1, curses.color_pair(1))
                        
                        prompt = "(Tekan tombol apapun untuk kembali ke Kota...)"
                        wm.stdscr.addstr(center_y + 3, max(0, (max_x - len(prompt)) // 2), prompt)
                        
                        wm.stdscr.refresh()
                    except curses.error: pass
                    stdscr.getch()
                unsaved_progress = True
                state = GameState.TOWN_HUB

if __name__ == "__main__":
    curses.wrapper(main)
