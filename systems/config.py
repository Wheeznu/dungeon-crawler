import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_CONFIG = {
    "difficulty": "NORMAL",
    "auto_save": True,
    "visual_fx": True,
    "log_lines": 12,
    "language": "ID"
}

config = DEFAULT_CONFIG.copy()

def load_settings():
    global config
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                config.update(data)
        except Exception:
            pass

def save_settings():
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception:
        pass
