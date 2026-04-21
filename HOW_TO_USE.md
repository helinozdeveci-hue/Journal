# 🐱 Therapy Cat - Anleitung

## Schnellstart

### 1. **Test-Daten erstellen** (zum Ausprobieren)
```bash
python chat_interface.py --create-test-data
```
Dies erstellt 3 Beispiel-Einträge mit Metriken für einen Test-Benutzer.

### 2. **Interface starten**
```bash
python chat_interface.py
```

## Interface bedienen

### 🔐 Schritt 1: Benutzer auswählen
```
THERAPY CAT - Journal Assistant
=====================================

BERÜHRTE BENUTZER IN DER DB:
  1. TestUser
  2. Neuer Benutzer
  0. Beenden

Wahl: 1  ← Schreibe Numer und Enter
```

### 📝 Schritt 2: Hauptmenü
Sobald Benutzer ausgewählt:
```
EINTRÄGE - Benutzer: TestUser
=====================================

3 Einträge gefunden:

  1. 2026-04-14 - War ein stressiger Tag heute... (5 Metriken)
  2. 2026-04-15 - Besserer Tag! Mit Freunden... (6 Metriken)
  3. 2026-04-16 - Heute ist produktiv Tag... (5 Metriken)

OPTIONEN:
  1. Eintrag auswählen
  2. Neuen Eintrag erstellen
  3. Mit Katze chatten (allgemein)
  4. Überblick von Katze
  0. Zurück
```

## 🎯 Was kann ich machen?

### **1. Eintrag auswählen** (Option 1)
- Zeigt alle Einträge
- Wähle einen aus mit Nummer
- Sehe alle Metriken des Eintrags
- Chat über diesen Eintrag mit Miau

### **2. Neuen Eintrag erstellen** (Option 2)
```
NEUEN EINTRAG ERSTELLEN
=====================================

Datum (Standard: 2026-04-16): [Enter = heute]
Notiz (Optional): Heute war ein guter Tag!
Metriken hinzufügen? (j/n): j
```

### **3. Metriken hinzufügen/ändern**
Nach Entry-Erstellung oder im Entry-Detail:
```
METRIK HINZUFÜGEN/ÄNDERN

VERFÜGBARE METRIKEN:

  1. stomach ache
  2. sad
  3. stress
  4. calm
  5. energy
  6. happy
  ... (20 insgesamt)

Metrik wählen: 3
Metrik: stress
Wert eingeben (1-5): 4
```

### **4. Mit Katze chatten** (Option 3)
```
CHAT MIT MIAU - Therapie-Katze

Was möchtest du der Katze sagen?
(Oder 'quit' zum Beenden)

>>> Ich fühle mich heute überfordert, was kannst du mir empfehlen?

Miau überlegt...

MIAU ANTWORTET:
=====================================

[Hier antwortet die KI basierend auf deinen Metriken und Notizen]
```

### **5. Überblick von Katze** (Option 4)
- Miau analysiert ALLE deine Einträge
- Gibt dir einen umfassenden Überblick
- Bezieht sich auf deine Trends über Zeit

### **6. Eintrag im Detail** (Nach Auswahl)
```
EINTRAG DETAIL - ID: 1

Datum: 2026-04-14
Notiz: War ein stressiger Tag heute, aber ich habe es geschafft!

METRIKEN (5 erfasst):
  calm: 2/5
  energy: 2/5
  sad: 3/5
  stomach ache: 4/5
  stress: 4/5

OPTIONEN:
  1. Mit Katze über diesen Eintrag chatten
  2. Metrik hinzufügen/ändern
  0. Zurück
```

## ⚙️ Verfügbare Metriken

Die App erfasst 20 verschiedene Metriken:

**Emotional:**
- sad, happy, angry, anxious, depressed, mood swings

**Körperlich:**
- energy, nausea, stomach ache

**Verhalten:**
- focus problems, attention problems, impulsive, aggressive, irritable, hyperactive

**Befindlichkeit:**
- calm, stress, interest in activities, excitable

## 🔒 Multi-User Support

- Jeder Benutzer hat **eigene Einträge**
- Keine Vermischung zwischen Usern
- Die KI kennt nur **deinen User's Daten**
- Vollständige Datentrennung

## 🚀 Erweiterte Features

### Nur für Entwickler

**Neue Metriken hinzufügen:**
```python
from db import create_metric
create_metric("meine-neue-metrik")
```

**Entry programmisch erstellen:**
```python
from db import create_entry, add_entry_value

entry_id = create_entry(
    date="2026-04-16",
    note="Mein Eintrag",
    created_by="TestUser"
)
add_entry_value(entry_id, metric_id=3, value=4)  # Z.B. Stress = 4
```

## 💡 Tips & Tricks

1. **Test-Daten löschen:** Die Datei `journal.db` löschen, dann `--create-test-data` erneut ausführen
2. **Mehrere User:** Jeden User mit anderem Namen erstellen - sie teilen sich keine Daten
3. **API aktivieren:** `pip install google-genai` um die KI-Funktionen zu nutzen
4. **Frühe Einträge anschauen:** Je mehr Daten, desto besser kann Miau Trends erkennen

## 🐛 Troubleshooting

### `ImportError: cannot import name 'genai'`
```bash
pip install google-genai
```

### `database is locked`
- Schließe alle Python-Prozesse
- Lösche ggfs. `journal.db-journal`

### Keine Einträge sichtbar?
```bash
python chat_interface.py --create-test-data
```

## 📋 Dateistruktur

```
journalApp/
├── db.py                    # Datenbank-Funktionen
├── test_gemini.py           # KI-Integration
├── chat_interface.py        # DICH HIER VERWENDEN!
├── seed_metrics.py          # Metriken initialisieren
├── journal.db              # Datenbank (wird auto erstellt)
└── HOW_TO_USE.md           # Diese Datei
```

## 🎯 Nächste Schritte

1. Test-Daten erstellen ✅
2. Interface starten ✅  
3. Mit deinem Benutzer einloggen
4. Neue Einträge erstellen
5. Mit Miau chatten
6. Deine Metriken verwalten

Viel Spaß mit deiner Therapie-Katze! 🐱💚
