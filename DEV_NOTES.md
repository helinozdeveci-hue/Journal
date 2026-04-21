# 🛠️ DEV_NOTES.md - Schnelle Referenz für Entwickler

## 📂 Dateistruktur

```
journalApp/
├── app.py              ← Hauptanwendung (CustomTkinter GUI)
├── db.py               ← Datenbankfunktionen (SQLite3)
├── test_gemini.py      ← AI Chat Integration (Gemini API)
├── user_config.py      ← User-Management & Config [21.04.2026]
├── seed_metrics.py     ← Beispiel-Metriken laden
├── chat_interface.py   ← (Legacy/Backup)
├── HOW_TO_USE.md       ← Benutzer-Anleitung
└── CHANGELOG.md        ← Änderungsprotokoll [21.04.2026]
```

## 🔑 Wichtigste Code Snippets

### 1️⃣ User abrufen
```python
from user_config import get_current_user, set_current_user

current_user = get_current_user()  # Gibt aktuellen User
set_current_user("Helin")          # Setzt neuen User
```

### 2️⃣ User-spezifische Entries aus DB
```python
from db import get_user_entries, get_entry_with_metrics

entries = get_user_entries(current_user, limit=50)
entry = get_entry_with_metrics(entry_id, current_user)
```

### 3️⃣ AI Chat mit User-Kontext
```python
from test_gemini import therapy_cat_general_chat

response = therapy_cat_general_chat(current_user, "How was your day?")
```

### 4️⃣ Config-Info debuggen
```python
from user_config import print_config_info

print_config_info()  # Zeigt User, Device-ID, Config-Pfad
```

## 📋 Multi-User Query Pattern

**WICHTIG**: Alle User-Querys MÜSSEN folgendes Pattern nutzen:

```python
# ❌ FALSCH:
WHERE created_by = ?
params = (username,)

# ✅ RICHTIG:
WHERE created_by = ? OR (created_by IS NULL AND ? = 'Standard')
params = (username, username)
```

**Grund**: NULL-Einträge gehören zu "Standard"-User (backward compatible)

## 🎯 Gemini API Wichtig

**Modell**: `gemini-3.1-flash-lite-preview` (nicht `gemini-2-flash`!)

**Korrekte API-Syntax**:
```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents=[
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=full_prompt)]
        )
    ]
)
```

**❌ NICHT nutzen**:
- `system_instruction=` (nicht vorhanden in dieser API)
- `config=GenerateContentConfig(...)` (verursacht Fehler)
- `top_k`, `thinking_config` (nicht für dieses Modell)

## 🔄 Typischer Workflow bei Änderungen

1. **Feature hinzufügen**
   - Code schreiben
   - `# [TT.MM.YYYY]` Kommentar hinzufügen
   - In `CHANGELOG.md` dokumentieren

2. **Bug fixen**
   - Fehler reproduzieren
   - Fix implementieren
   - Test durchführen
   - Mit Datum kennzeichnen

3. **Testing**
   - App mit frischem User starten
   - Login-Dialog testen
   - User-Wechsel prüfen
   - Multi-User Isolation checken

## 📍 Config-Datei Location

```
Linux/Mac:   ~/.journalapp/config.json
Windows:     C:\Users\[USERNAME]\.journalapp\config.json
```

**Format**:
```json
{
    "version": "1.0",
    "username": "Dein Name",
    "device_id": "MAC-address-uuid",
    "created_at": "2026-04-21T10:30:00",
    "last_login": "2026-04-21T15:45:00"
}
```

## 🚀 Häufige Tasks

### Task: Neuen User zur DB hinzufügen
```python
from user_config import get_current_user, set_current_user
from db import create_entry

new_user = "Helia"
set_current_user(new_user)
create_entry(new_user, "2026-04-21", "First entry")
```

### Task: Alle Entries eines Users lesen
```python
from db import get_user_entries
from user_config import get_current_user

current_user = get_current_user()
entries = get_user_entries(current_user)
for entry in entries:
    print(f"{entry['date']}: {entry['note']}")
```

### Task: Metriken für User abrufen
```python
from db import get_user_todays_metrics
from user_config import get_current_user

current_user = get_current_user()
metrics = get_user_todays_metrics(current_user)
for metric in metrics:
    print(f"{metric['metric_name']}: {metric['value']}")
```

## 🐛 Häufige Fehler

| Fehler | Ursache | Lösung |
|--------|--------|--------|
| `KeyError: 'value'` | Falscher Feldname in Query | Query sollte `ev.value as value` haben |
| `Gemini 404 Error` | Falsches Modell | Nutze `gemini-3.1-flash-lite-preview` |
| `DB locked` | Mehrere Connections | Eine DB-Connection pro Thread |
| `User not found` | User nicht gesetzt | Rufe `set_current_user()` auf |
| `OSError in config` | ~/.journalapp/ existiert nicht | Wird auto-erstellt beim Start |

## 📚 Dependencies

```
customtkinter>=5.0        # GUI Framework
google-genai>=0.3.0       # Gemini API
python>=3.13             # Python Version
sqlite3                  # Built-in, keine Installation nötig
```

## ✅ Checkliste for Neue Features

- [ ] Code geschrieben
- [ ] `# [TT.MM.YYYY]` Kommentare hinzugefügt
- [ ] In `CHANGELOG.md` dokumentiert  
- [ ] Mit aktuellem User getestet
- [ ] Multi-User Isolation überprüft
- [ ] Fehlerbehandlung implementiert
- [ ] DB-Migrationn (falls nötig) durchgeführt

---

**Zuletzt aktualisiert**: [21.04.2026]
**Autor**: Copilot & Helin
