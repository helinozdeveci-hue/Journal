import json 
import os 
from pathlib import Path
from datetime import datetime
import uuid

from db import get_connection, register_user

# Konfigurationsordner im Home-Verzeichnis des Nutzers anlegen (wird beim Import erstellt falls nicht vorhanden)
APP_CONFIG_DIR = Path.home() / ".journalapp"
APP_CONFIG_DIR.mkdir(exist_ok=True) # kein Fehler wenn der Ordner bereits existiert
CONFIG_FILE = APP_CONFIG_DIR / "config.json"

# eindeutige Geräte-ID anhand der MAC-Adresse erzeugen
def get_device_id() -> str:
    return str(uuid.getnode())

# Konfiguration aus der JSON-Datei laden, bei Fehler Standardwerte zurückgeben
def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Config: {e}")
            return get_default_config()
    return get_default_config() # Datei existiert noch nicht → Standardwerte

# Standardkonfiguration für neue Installationen
def get_default_config() -> dict:
    return {
        "version": "1.0",
        "username": None,          # wird nach dem ersten Login gesetzt
        "device_id": get_device_id(),
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }

# Konfiguration als JSON-Datei speichern und Last-Login-Zeitstempel aktualisieren
def save_config(config: dict) -> bool:
    try:
        config["last_login"] = datetime.now().isoformat()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False) # ensure_ascii=False für Umlaute
        return True
    except Exception as e:
        print(f"Fehler beim Speichern der Config: {e}")
        return False

# zuletzt gespeicherten Benutzernamen aus der Config lesen (für Auto-Fill beim Login)
def get_saved_username() -> str | None:
    config = load_config()
    return config.get("username")

# Benutzernamen in der Konfigurationsdatei speichern
def save_username(username: str) -> bool:
    config = load_config()
    config["username"] = username
    return save_config(config)

# Benutzerwechsel: einfach Login mit neuem Benutzernamen und PIN
def switch_user(new_username: str, pin: int) -> int | None:
    return login_user(new_username, pin)

# neuen Benutzer in der Datenbank registrieren (delegiert an db.py)
def register_new_user(username: str, pin: int) -> bool:
    return register_user(username, pin)

# Benutzer anhand von Username und PIN in der DB prüfen, gibt user_id zurück oder None
def login_user(username: str, pin: int) -> int | None:
    with get_connection() as conn:
        result = conn.execute(
            "SELECT id FROM users WHERE username = ? AND pin = ?",
            (username, pin)
        ).fetchone()
    if result:
        return result[0] # nur die ID zurückgeben, nicht die ganze Zeile
    return None

# prüft ob das aktuelle Gerät mit der gespeicherten Geräte-ID übereinstimmt
def device_id_known() -> bool:
    config = load_config()
    if config.get("device_id") == get_device_id():
        return True
    return False

# Config-Informationen zur Fehlersuche in der Konsole ausgeben (wird nach dem Login aufgerufen)
def print_config_info():
    config = load_config()
    print(f"\n{'='*50}")
    print(f"App Config Location: {CONFIG_FILE}")
    print(f"Current User: {config.get('username', 'NICHT GESETZT')}")
    print(f"Device ID: {config.get('device_id')}")
    print(f"Last Login: {config.get('last_login', 'Nie')}")
    print(f"{'='*50}\n")