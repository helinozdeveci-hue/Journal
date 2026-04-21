<<<<<<< HEAD
# 📔 Journal App - Entwickler Tagebuch

## [21.04.2026] - User-Management & Security System

### ✨ Neue Features

#### 1. **Lokales User-Management System** (`user_config.py`)
- [21.04.2026] Neue Datei erstellt für User-Authentifikation
- [21.04.2026] Config-Datei: `~/.journalapp/config.json`
- [21.04.2026] Speichert: Username, Device-ID, Timestamps
- [21.04.2026] Geräte-Erkennung via MAC-Adresse (`uuid.getnode()`)

#### 2. **Login-System beim App-Start**
- [21.04.2026] Login-Dialog beim ersten Start
- [21.04.2026] User wird gespeichert in lokalem Config
- [21.04.2026] Beim nächsten Start wird User automatisch geladen
- [21.04.2026] Debug-Info wird in Terminal ausgegeben

#### 3. **User-Wechsel Feature**
- [21.04.2026] 👤 Button in Header (blue #4A90E2)
- [21.04.2026] Erlaubt Wechsel zu anderem User
- [21.04.2026] Aktualisiert alle Entries für neuen User
- [21.04.2026] Neue Entries werden automatisch dem User zugeordnet

### 🔒 Security Improvements

- [21.04.2026] Entries sind jetzt User-spezifisch (DB-Filter)
- [21.04.2026] User kann nur eigene Entries sehen
- [21.04.2026] Device-ID wird zur Tracking/Audit gespeichert
- [21.04.2026] Config basiert auf lokalem ~/.journalapp/

### 📝 Geänderte Dateien

#### `app.py`
- [21.04.2026] Import: `from user_config import get_current_user, set_current_user, print_config_info`
- [21.04.2026] `__init__()`: Lade oder frage nach User beim Start
- [21.04.2026] Neue Methode: `_show_login_dialog()` - Willkommens-Dialog
- [21.04.2026] Neue Methode: `_open_user_switch()` - User-Wechsel Dialog
- [21.04.2026] Header Button: `👤 [Username]` zum Wechseln
- [21.04.2026] Entfernt: Hardcoded `current_user = "Standard"`

#### `user_config.py` (NEU)
- [21.04.2026] Komplettes neues Modul für User-Management
- [21.04.2026] Funktionen:
  - `get_device_id()` - Eindeutige Geräte-ID
  - `load_config()` - Lade Konfiguration
  - `get_default_config()` - Standard-Config
  - `save_config()` - Speichere Konfiguration
  - `get_current_user()` - Aktueller User
  - `set_current_user()` - User setzen
  - `switch_user()` - User wechseln
  - `print_config_info()` - Debug-Info

### 📊 Config-Struktur

```json
{
    "version": "1.0",
    "username": "Helin",
    "device_id": "123456789abc",
    "created_at": "2026-04-21T10:30:00",
    "last_login": "2026-04-21T15:45:00"
}
```

### 🎯 Verwendung

1. **Erste Nutzung**: App startet → Login-Dialog → Name eingeben
2. **Weitere Nutzung**: App lädt User automatisch
3. **User wechseln**: Klick auf 👤 Button → Neuer Name → Fertig
4. **Debug-Info**: `print_config_info()` gibt Status in Terminal

### ⚙️ Technische Details

- Config-Datei: `~/.journalapp/config.json`
- Geräte-ID: MAC-Adresse des Systems
- Timestamps: ISO-Format (2026-04-21T...)
- DB-Filter: Alle Queries filtern nach `created_by = current_user`

### 🚀 Nächste Schritte (Optional)

- [ ] PIN-Schutz hinzufügen
- [ ] Backup/Export der Daten
- [ ] Multi-Device Sync (Cloud)
- [ ] Passwort-Hashing für mehr Sicherheit

---

**Status**: ✅ Fertig & Getestet
**Autor**: Copilot
**Datum**: 21.04.2026
=======
# 📔 Journal App - Entwickler Tagebuch

## [21.04.2026] - User-Management & Security System

### ✨ Neue Features

#### 1. **Lokales User-Management System** (`user_config.py`)
- [21.04.2026] Neue Datei erstellt für User-Authentifikation
- [21.04.2026] Config-Datei: `~/.journalapp/config.json`
- [21.04.2026] Speichert: Username, Device-ID, Timestamps
- [21.04.2026] Geräte-Erkennung via MAC-Adresse (`uuid.getnode()`)

#### 2. **Login-System beim App-Start**
- [21.04.2026] Login-Dialog beim ersten Start
- [21.04.2026] User wird gespeichert in lokalem Config
- [21.04.2026] Beim nächsten Start wird User automatisch geladen
- [21.04.2026] Debug-Info wird in Terminal ausgegeben

#### 3. **User-Wechsel Feature**
- [21.04.2026] 👤 Button in Header (blue #4A90E2)
- [21.04.2026] Erlaubt Wechsel zu anderem User
- [21.04.2026] Aktualisiert alle Entries für neuen User
- [21.04.2026] Neue Entries werden automatisch dem User zugeordnet

### 🔒 Security Improvements

- [21.04.2026] Entries sind jetzt User-spezifisch (DB-Filter)
- [21.04.2026] User kann nur eigene Entries sehen
- [21.04.2026] Device-ID wird zur Tracking/Audit gespeichert
- [21.04.2026] Config basiert auf lokalem ~/.journalapp/

### 📝 Geänderte Dateien

#### `app.py`
- [21.04.2026] Import: `from user_config import get_current_user, set_current_user, print_config_info`
- [21.04.2026] `__init__()`: Lade oder frage nach User beim Start
- [21.04.2026] Neue Methode: `_show_login_dialog()` - Willkommens-Dialog
- [21.04.2026] Neue Methode: `_open_user_switch()` - User-Wechsel Dialog
- [21.04.2026] Header Button: `👤 [Username]` zum Wechseln
- [21.04.2026] Entfernt: Hardcoded `current_user = "Standard"`

#### `user_config.py` (NEU)
- [21.04.2026] Komplettes neues Modul für User-Management
- [21.04.2026] Funktionen:
  - `get_device_id()` - Eindeutige Geräte-ID
  - `load_config()` - Lade Konfiguration
  - `get_default_config()` - Standard-Config
  - `save_config()` - Speichere Konfiguration
  - `get_current_user()` - Aktueller User
  - `set_current_user()` - User setzen
  - `switch_user()` - User wechseln
  - `print_config_info()` - Debug-Info

### 📊 Config-Struktur

```json
{
    "version": "1.0",
    "username": "Helin",
    "device_id": "123456789abc",
    "created_at": "2026-04-21T10:30:00",
    "last_login": "2026-04-21T15:45:00"
}
```

### 🎯 Verwendung

1. **Erste Nutzung**: App startet → Login-Dialog → Name eingeben
2. **Weitere Nutzung**: App lädt User automatisch
3. **User wechseln**: Klick auf 👤 Button → Neuer Name → Fertig
4. **Debug-Info**: `print_config_info()` gibt Status in Terminal

### ⚙️ Technische Details

- Config-Datei: `~/.journalapp/config.json`
- Geräte-ID: MAC-Adresse des Systems
- Timestamps: ISO-Format (2026-04-21T...)
- DB-Filter: Alle Queries filtern nach `created_by = current_user`

### 🚀 Nächste Schritte (Optional)

- [ ] PIN-Schutz hinzufügen
- [ ] Backup/Export der Daten
- [ ] Multi-Device Sync (Cloud)
- [ ] Passwort-Hashing für mehr Sicherheit

---

**Status**: ✅ Fertig & Getestet
**Autor**: Copilot
**Datum**: 21.04.2026
>>>>>>> f4b33033418b049f54446c3066f199365ef0bc9e
