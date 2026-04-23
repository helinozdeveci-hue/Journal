#AIzaSyAxsamRhFettu1g30KLBpncTXSc12npjIg
from google import genai
from google.genai import types
from db import (
    get_user_entries, get_entry_with_metrics, get_user_todays_metrics, 
    get_user_metrics_raw_data, list_users, list_metrics
)
import json
from datetime import date

# Config
API_KEY = "AIzaSyAxsamRhFettu1g30KLBpncTXSc12npjIg"
MODEL = "gemini-3.1-flash-lite-preview"  # Model Name

# Instructions for the Therapy Cat - this will be the system prompt for all interactions
THERAPY_CAT_SYSTEM_INSTRUCTION = """
Du bist Miausi, eine liebevolle und einfühlsame Therapie-Katze mit tiefem Verständnis für menschliche Emotionen und Wohlbefinden.

**DEINE ROLLE:**
- Du bist ein unterstützender neutraler Begleiter, kein Arzt oder Therapeut
- Deine Antworten sollten warm, ermutigend und nicht-wertend sein
- Du verfügst über Zugang zu persönlichen Metriken des Nutzers (Stimmung, Energie, Stress, etc.)
- Du verwendest diese Daten, um personalisierte Vorschläge für einen gesunden Tag zu geben

**DEIN ANSATZ:**
1. Begrüße den Nutzer mit Namen, wenn vorhanden
2. Erkenne die aktuellen emotionalen/physischen Zustände basierend auf den Metriken
3. Analysiere Trends über Zeit, um Muster zu erkennen
4. Gebe konkrete, umsetzbare Vorschläge, Ratschläge oder Unterstützung basierend auf den Zusatzwerten

**PERSONALISIERUNG DURCH METRIKEN:**
Du erhältst Zugang zu folgenden Kategorien:
- Emotionale Metriken: sad, happy, angry, anxious, depressed, mood swings, exciteable
- Körperliche Metriken: energy, nausea, stomach ache
- Verhaltensbezogene Metriken: focus problems, attention problems, impulsive, aggressive, forgetfulness, hyperactive, 
- Befindlichkeitsmetriken: calm, stress, interest in activities, irritable

**GENERIERUNG VON ZUSATZWERTEN:**
(folgt später, hier Logik implementieren)

**TONALITÄT:**
- Wärm, verständnisvoll, motivierend
- Nutze gelegentliche 🐱 katzen-bezogene Metaphern
- Sei präsent und aufmerksam, nicht distanziert
- Validiere die Gefühle, bevor du Vorschläge machst

**BEISPIEL-OUTPUT STRUKTUR:**
"Hallo [Name]! *Schnurr* 🐱
Ich sehe, dass du heute mit [X Metrik] kämpfst. Das ist völlig normal und ich bin hier, um dich zu unterstützen.

Basierend auf deinen heutigen Werten schlage ich dir vor:
1. [Konkrete Aktion 1]
2. [Konkrete Aktion 2]
3. [Konkrete Aktion 3]

Wie fühlt sich das für dich an?"

**WARNSIGNALE:**
Wenn schwere psychische Probleme erkannt werden (Depression > 4, Suizidgedanken erwähnt):
- Sei unterstützend, aber weise auf professionelle Hilfe hin
- Biete sofort Ressourcen an (Hotlines, Online-Therapie, etc.)
"""

# initialize Gemini client
client = genai.Client(api_key=API_KEY)

# 
def format_user_entries(created_by: str) -> str:
    
    entries = get_user_entries(created_by)
    
    entries_text = f"""
=== ALLE JOURNAL-EINTRÄGE FÜR {created_by.upper()} ===
Insgesamt: {len(entries)} Einträge
"""
    
    for entry in entries:
        entries_text += f"""
--- Eintrag vom {entry['date']} ---
Notiz: {entry['note'] or '(keine Notiz)'}
Metriken:
"""
        if entry['metrics']:
            for metric_key, value in sorted(entry['metrics'].items()):
                entries_text += f"  {metric_key}: {value}/5\n"
        else:
            entries_text += "  (keine Metriken erfasst)\n"
    
    return entries_text


def format_single_entry(entry_id: int, created_by: str) -> str | None:
    """
    Formatiert einen einzelnen Entry mit allen Details.
    SICHERHEIT: Überprüft, dass dieser Entry vom User stammt.
    
    Args:
        entry_id: Die ID des Entries
        created_by: Der Nutzer-Identifier (Sicherheits-Check)
        
    Returns:
        Formatierter String mit Entry-Details, oder None wenn nicht gefunden
    """
    entry = get_entry_with_metrics(entry_id, created_by=created_by)
    
    if not entry:
        return None
    
    entry_text = f"""
=== EINTRAG DETAILS ===
Datum: {entry['date']}
Erstellt von: {entry['created_by']}
Notiz: {entry['note'] or '(keine Notiz)'}

METRIKEN ({len(entry['metrics'])} erfasst):
"""
    
    if entry['metrics']:
        for metric_key, value in sorted(entry['metrics'].items()):
            entry_text += f"  {metric_key}: {value}/5\n"
    else:
        entry_text += "  (keine Metriken)\n"
    
    return entry_text


def format_user_metrics_today(created_by: str) -> str:
    """
    Formatiert die heutigen Metriken eines Users.
    
    Args:
        created_by: Der Nutzer-Identifier
        
    Returns:
        Formatierter String mit heutigen Metriken
    """
    todays_metrics = get_user_todays_metrics(created_by)
    
    metrics_text = f"""
=== {created_by.upper()} - METRIKEN HEUTE ({date.today()}) ===
"""
    
    if todays_metrics:
        for key, value in sorted(todays_metrics.items()):
            metrics_text += f"- {key}: {value}/5\n"
    else:
        metrics_text += "Noch keine Metriken heute erfasst.\n"
    
    return metrics_text


def format_user_metrics_trend(created_by: str, days: int = 30) -> str:
    """
    Formatiert die Metrik-Trends eines Users über Zeit.
    
    Args:
        created_by: Der Nutzer-Identifier
        days: Anzahl der Tage zur Analyse
        
    Returns:
        Formatierter String mit Metrik-Trends
    """
    metrics_raw = get_user_metrics_raw_data(created_by, days=days)
    
    trend_text = f"""
=== {created_by.upper()} - METRIK TRENDS (letzte {days} Tage) ===
"""
    
    if metrics_raw:
        for key in sorted(metrics_raw.keys()):
            data = metrics_raw[key]
            values = data['values']
            dates = data['dates']
            trend_text += f"- {key}: {values} (Daten auf {len(values)} Tagen)\n"
    else:
        trend_text += "Keine Trend-Daten verfügbar.\n"
    
    return trend_text


def calculate_additional_values(metrics: dict) -> dict:
    """
    PLATZHALTER: Hier können später Zusatzwert-Berechnungen erfolgen.
    Diese Funktion wird vom Nutzer mit eigener Logik gefüllt.
    
    Args:
        metrics: Dictionary mit Metrik-Keys und Werten (1-5)
        
    Returns:
        Dictionary mit benutzerdefinierten Zusatzwerten
    """
    # TODO: Nutzer definiert hier die Gewichtung und Berechnung von Zusatzwerten
    # z.B. Indizes, Trends, Risk-Levels, etc.
    
    additional_values = {}
    # ENTWURF:
    # additional_values['stress_index'] = ...
    # additional_values['energy_balance'] = ...
    # additional_values['emotional_stability'] = ...
    
    return additional_values


# ===== HAUPTFUNKTIONEN =====

def therapy_cat_overview(created_by: str) -> str:
    """
    Die Katze zeigt einen Überblick über ALLE Einträge eines Users.
    
    Args:
        created_by: Der Nutzer-Identifier (MUSS match created_by in DB)
        
    Returns:
        Antwort der Therapie-Katze als String
    """
    all_entries = format_user_entries(created_by)
    today_metrics = format_user_metrics_today(created_by)
    trends = format_user_metrics_trend(created_by, days=30)
    
    full_prompt = f"""{THERAPY_CAT_SYSTEM_INSTRUCTION}

[USER-KONTEXT]
Nutzer: {created_by}
Anfrage: Überblick über alle meine Journal-Einträge und Metriken

{all_entries}

{today_metrics}

{trends}
"""
    
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=full_prompt)],
                )
            ],
        )
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API Error: {str(e)}")


def therapy_cat_analyze_entry(entry_id: int, created_by: str, user_message: str = "") -> str:
    """
    Die Katze analysiert einen EINZELNEN Entry mit seinen Metriken.
    SICHERHEIT: Der Entry muss vom User stammen (created_by Check).
    
    Args:
        entry_id: Die ID des spezifischen Entry
        created_by: Der Nutzer-Identifier (Sicherheits-Check)
        user_message: Optional - zusätzliche Frage des Users
        
    Returns:
        Antwort der Therapie-Katze als String
    """
    # SICHERHEIT: Prüfe ob dieser Entry vom User stammt
    entry_details = format_single_entry(entry_id, created_by)
    
    if not entry_details:
        return f"Fehler: Entry #{entry_id} für Nutzer '{created_by}' nicht gefunden. Zugriff verweigert oder Entry existiert nicht."
    
    today_metrics = format_user_metrics_today(created_by)
    trends = format_user_metrics_trend(created_by, days=30)
    
    full_prompt = f"""{THERAPY_CAT_SYSTEM_INSTRUCTION}

[USER-KONTEXT]
Nutzer: {created_by}
Aktion: Analysiere diesen Entry im Detail

{entry_details}

{today_metrics}

{trends}

Nutzer's zusätzliche Frage/Kommentar: {user_message or '(keine)'}
"""
    
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=full_prompt)],
                )
            ],
        )
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API Error: {str(e)}")


def therapy_cat_general_chat(created_by: str, user_message: str) -> str:
    """
    Freier Chat mit der Therapie-Katze - basierend auf heutigen Metriken und Trends.
    
    Args:
        created_by: Der Nutzer-Identifier
        user_message: Die Nachricht des Users an die Katze
        
    Returns:
        Antwort der Therapie-Katze als String
    """
    today_metrics = format_user_metrics_today(created_by)
    trends = format_user_metrics_trend(created_by, days=30)
    
    # Kombiniere System-Anweisung mit dem User-Input
    full_prompt = f"""{THERAPY_CAT_SYSTEM_INSTRUCTION}

[USER-KONTEXT]
Nutzer: {created_by}
Nachricht: {user_message}

{today_metrics}

{trends}
"""
    
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=full_prompt)],
                )
            ],
        )
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API Error: {str(e)}")


# ===== BEISPIEL NUTZUNG =====

if __name__ == "__main__":
    # Beispiel: Multi-User Support mit created_by
    
    print("=" * 70)
    print("THERAPY CAT - Multi-User Journal Assistant")
    print("=" * 70)
    
    # ===== EXAMPLE 1: Überblick über alle Einträge eines Users =====
    user_name = "Alex"
    print(f"\n[BEISPIEL 1] Überblick für User: {user_name}")
    print("-" * 70)
    # Entkommentiere um zu testen (braucht Daten in DB):
    # response = therapy_cat_overview(created_by=user_name)
    # print(f"Miausi:\n{response}\n")
    print("(Test aktivieren wenn Testdaten in DB vorhanden sind)")
    
    # ===== EXAMPLE 2: Analyse eines einzelnen Entry =====
    print(f"\n[BEISPIEL 2] Analyse eines spezifischen Entry")
    print("-" * 70)
    # Beispiel: Entry mit ID 1 für User "Alex"
    # response = therapy_cat_analyze_entry(
    #     entry_id=1,
    #     created_by="Alex",
    #     user_message="Wie habe ich mich damals gefühlt?"
    # )
    # print(f"Miausi:\n{response}\n")
    print("(Test aktivieren: therapy_cat_analyze_entry(entry_id=1, created_by='Alex'))")
    
    # ===== EXAMPLE 3: Freier Chat mit der Katze =====
    print(f"\n[BEISPIEL 3] Freier Chat mit der Katze")
    print("-" * 70)
    chat_message = "Ich fühle mich heute überfordert. Was kannst du mir vorschlagen?"
    print(f"User ({user_name}): {chat_message}")
    # response = therapy_cat_general_chat(
    #     created_by=user_name,
    #     user_message=chat_message
    # )
    # print(f"Miausi:\n{response}\n")
    print("(Test aktivieren wenn Testdaten in DB vorhanden sind)")
    
    print("\n" + "=" * 70)
    print("MULTI-USER SICHERHEIT:")
    print("- Jede Funktion nutzt 'created_by' Parameter")
    print("- Entries werden nur für den spezifizierten User geladen")
    print("- Keine Vermischung zwischen verschiedenen Usern")
    print("=" * 70)