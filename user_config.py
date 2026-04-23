# User-Management und Config-Speicherung System

import json
import os
from pathlib import Path
from datetime import datetime
import uuid

# Config-Verzeichnis Setup
APP_CONFIG_DIR = Path.home() / ".journalapp"
APP_CONFIG_DIR.mkdir(exist_ok=True)
CONFIG_FILE = APP_CONFIG_DIR / "config.json"

# Geräte-ID generieren (MAC-Adresse basiert)
def get_device_id() -> str:
    return str(uuid.getnode())

# Config laden oder erstellen
def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Config: {e}")
            return get_default_config()
    return get_default_config()

# Standard-Config erstellen
def get_default_config() -> dict:
    return {
        "version": "1.0",
        "username": None,
        "device_id": get_device_id(),
        "created_at": datetime.now().isoformat(),
        "last_login": None,
    }

# Config speichern
def save_config(config: dict) -> bool:
    try:
        config["last_login"] = datetime.now().isoformat()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            # alle möglichen daten sollen in der config gespeichert werden
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Fehler beim Speichern der Config: {e}")
        return False

# User beim Start abrufen
def get_current_user() -> str | None:
    config = load_config()
    return config.get("username")

# User speichern
def set_current_user(username: str) -> bool:
    config = load_config()
    config["username"] = username
    return save_config(config)

# Benutzer wechseln
def switch_user(new_username: str) -> bool:
    return set_current_user(new_username)

# Config-Info anzeigen (für Debugging)
def print_config_info():
    config = load_config()
    print(f"\n{'='*50}")
    print(f"App Config Location: {CONFIG_FILE}")
    print(f"Current User: {config.get('username', 'NICHT GESETZT')}")
    print(f"Device ID: {config.get('device_id')}")
    print(f"Last Login: {config.get('last_login', 'Nie')}")
    print(f"{'='*50}\n")
