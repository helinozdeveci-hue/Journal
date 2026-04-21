# [21.04.2026] User-Management und Config-Speicherung System
"""
Handles user authentication and local config management.
Speichert User-Daten lokal für Offline-Nutzung mit Geräte-Erkennung.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import uuid

# [21.04.2026] Config-Verzeichnis Setup
APP_CONFIG_DIR = Path.home() / ".journalapp"
APP_CONFIG_DIR.mkdir(exist_ok=True)
CONFIG_FILE = APP_CONFIG_DIR / "config.json"

# [21.04.2026] Geräte-ID generieren (MAC-Adresse basiert)
def get_device_id() -> str:
    """Generate unique device identifier based on MAC address"""
    return str(uuid.getnode())

# [21.04.2026] Config laden oder erstellen
def load_config() -> dict:
    """Lade existierende Config oder erstelle neue"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Config: {e}")
            return get_default_config()
    return get_default_config()

# [21.04.2026] Standard-Config erstellen
def get_default_config() -> dict:
    """Erstelle Standard-Config"""
    return {
        "version": "1.0",
        "username": None,
        "device_id": get_device_id(),
        "created_at": datetime.now().isoformat(),
        "last_login": None,
    }

# [21.04.2026] Config speichern
def save_config(config: dict) -> bool:
    """Speichere Config in JSON-Datei"""
    try:
        config["last_login"] = datetime.now().isoformat()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Fehler beim Speichern der Config: {e}")
        return False

# [21.04.2026] User beim Start abrufen
def get_current_user() -> str | None:
    """Gib aktuellen User aus Config zurück"""
    config = load_config()
    return config.get("username")

# [21.04.2026] User speichern
def set_current_user(username: str) -> bool:
    """Speichere aktuellen User in Config"""
    config = load_config()
    config["username"] = username
    return save_config(config)

# [21.04.2026] Benutzer wechseln
def switch_user(new_username: str) -> bool:
    """Wechsle zu anderem User"""
    return set_current_user(new_username)

# [21.04.2026] Config-Info anzeigen (für Debugging)
def print_config_info():
    """Zeige Config-Informationen"""
    config = load_config()
    print(f"\n{'='*50}")
    print(f"App Config Location: {CONFIG_FILE}")
    print(f"Current User: {config.get('username', 'NICHT GESETZT')}")
    print(f"Device ID: {config.get('device_id')}")
    print(f"Last Login: {config.get('last_login', 'Nie')}")
    print(f"{'='*50}\n")
