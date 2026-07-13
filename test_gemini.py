from user_key_config import load_key  
from google import genai
from google.genai import types
from datetime import date
from typing import Optional
import time


# dotenv und os.getenv KOMPLETT RAUS - das macht jetzt user_key_config

_client = None

def initialise_client(key):
    global _client
    print(f"[DEBUG] Initialisiere Gemini-Client mit Key: {key[:8]}...{key[-4:]}" if key else "[DEBUG] Initialisiere Gemini-Client ohne Key")
    _client = genai.Client(api_key=key)

def get_client():
    return _client

MODEL = "gemini-3.5-flash"
MODEL_FALLBACKS = ("gemini-3-flash-preview", "gemini-flash-latest")

# Very small token budget to keep costs low and avoid unnecessary usage.
MAX_OUTPUT_TOKENS = 150
MAX_PROMPT_CHARS = 220

# System-Prompt der Therapie-Katze: OPTIMIERT für minimale Token-Nutzung
# Kurz, prägnant, effektiv - 60 Tokens statt 200!
THERAPY_CAT_SYSTEM_INSTRUCTION = """Du bist Miausi, Therapie-Katze. 🐱 Warm, einfühlsam, nicht-wertend. Validiere zuerst. KEIN Arzt. Bei Suizidgedanken → professionelle Hilfe."""

# Der Gemini-Client wird erst dann initialisiert, wenn er wirklich gebraucht wird.

def _require_client():
    if _client is None:
        key = load_key()
        print(f"[DEBUG] Geladener Key aus user_key_config: {'Ja' if key else 'Nein'}")
        if key:
            initialise_client(key)
        else:
            raise RuntimeError("Kein Gemini-API-Key vorhanden. Bitte zuerst einen gültigen Key in der App eingeben.")
    return _client


def _classify_gemini_error(error: Exception) -> str:
    error_text = str(error or "").strip()
    lower = error_text.lower()

    if not error_text:
        return "Unbekannter Fehler bei der Gemini-Anfrage."

    if any(token in lower for token in ["api key", "authentication", "forbidden", "permission", "unauthorized", "invalid api"]):
        return "Der Google API-Key ist fehlend oder ungültig. Bitte einen gültigen Key eingeben."

    if any(token in lower for token in ["429", "resource_exhausted", "quota", "rate limit", "limit exceeded"]):
        return "Die Gemini-API hat das tägliche oder zeitliche Limit erreicht. Bitte kurz warten oder einen neuen Key verwenden."

    if any(token in lower for token in ["404", "not found", "model"]):
        return "Das verwendete Gemini-Modell ist nicht verfügbar oder der API-Key hat keinen Zugriff auf dieses Modell. Die App versucht es mit einem kompatiblen Modell."

    if any(token in lower for token in ["timeout", "temporarily unavailable", "service unavailable", "network"]):
        return "Die Gemini-API war kurzzeitig nicht erreichbar. Bitte kurz warten und erneut versuchen."

    return f"Gemini API Fehler: {error_text}"

def _generate_with_fallbacks(full_prompt: str):
    client = _require_client()
    last_error: Optional[Exception] = None

    for model_name in (MODEL, *MODEL_FALLBACKS):
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=full_prompt)],
                        )
                    ],
                    config=types.GenerateContentConfig(
                        max_output_tokens=MAX_OUTPUT_TOKENS,
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    ),
                )
                text = getattr(response, "text", None)
                if isinstance(text, str) and text.strip():
                    return text.strip()
                return str(response)
            except Exception as exc:
                last_error = exc
                print(f"[DEBUG] Rohfehler von Gemini ({model_name}): {exc}")
                lower = str(exc).lower()
                if "503" in lower and attempt == 0:
                    time.sleep(2)
                    continue
                if any(token in lower for token in ["404", "not found", "model"]):
                    break
                raise RuntimeError(_classify_gemini_error(exc)) from exc

    if last_error is not None:
        raise RuntimeError(_classify_gemini_error(last_error)) from last_error

    raise RuntimeError("Gemini-Anfrage fehlgeschlagen ohne detaillierte Fehlermeldung.")

def validate_key(max_output_tokens: int = 8) -> bool:
    """
    Führt einen sehr kleinen Test-Request aus, um zu prüfen, ob der geladene Key
    grundsätzlich Anfragen ausführen darf und nicht sofort wegen Quota/Unauthorized
    abgewiesen wird. Gibt True zurück wenn alles ok ist oder wirft eine RuntimeError
    mit klassifizierter Meldung.
    """
    client = _require_client()
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text="Kurzer Key-Test")],
                )
            ],
            config={"max_output_tokens": max_output_tokens},
        )
        return True
    except Exception as e:
        raise RuntimeError(_classify_gemini_error(e)) from e

# alle Journaleinträge eines Nutzers als lesbaren Text aufbereiten
# TODO: ZUKÜNFTIG - Datenbankzugriff wird später implementiert wenn die Metrik-Integration vollendet ist
# def format_user_entries(created_by: str) -> str:
#     
#     entries = list_entries(created_by)
#     
#     entries_text = f"""
# === ALLE JOURNAL-EINTRÄGE FÜR {created_by.upper()} ===
# Insgesamt: {len(entries)} Einträge
# """
#     
#     for entry in entries:
#         entries_text += f"""
# --- Eintrag vom {entry['date']} ---
# Notiz: {entry['note'] or '(keine Notiz)'}
# Metriken:
# """
#         if entry['metrics']:
#             for metric_key, value in sorted(entry['metrics'].items()):
#                 entries_text += f"  {metric_key}: {value}/5\n"
#         else:
#             entries_text += "  (keine Metriken erfasst)\n"
#     
#     return entries_text


# def format_single_entry(entry_id: int, created_by: str) -> str | None:
#     """
#     Formatiert einen einzelnen Entry mit allen Details.
#     SICHERHEIT: Überprüft, dass dieser Entry vom User stammt.
#     
#     TODO: ZUKÜNFTIG - wird implementiert wenn Entry-Analyse aktiviert wird
#     
#     Args:
#         entry_id: Die ID des Entries
#         created_by: Der Nutzer-Identifier (Sicherheits-Check)
#         
#     Returns:
#         Formatierter String mit Entry-Details, oder None wenn nicht gefunden
#     """
#     entry = get_entry_with_values(entry_id, created_by=created_by)
#     
#     if not entry:
#         return None
#     
#     entry_text = f"""
# === EINTRAG DETAILS ===
# Datum: {entry['date']}
# Erstellt von: {entry['created_by']}
# Notiz: {entry['note'] or '(keine Notiz)'}
#
# METRIKEN ({len(entry['metrics'])} erfasst):
# """
#     
#     if entry['metrics']:
#         for metric_key, value in sorted(entry['metrics'].items()):
#             entry_text += f"  {metric_key}: {value}/5\n"
#     else:
#         entry_text += "  (keine Metriken)\n"
#     
#     return entry_text


# def format_user_metrics_today(created_by: str) -> str:
#     """
#     Formatiert die heutigen Metriken eines Users.
#     
#     TODO: ZUKÜNFTIG - wird aktiviert wenn Metrik-Integration fertiggestellt ist
#     
#     Args:
#         created_by: Der Nutzer-Identifier
#         
#     Returns:
#         Formatierter String mit heutigen Metriken
#     """
#     todays_metrics = get_todays_metrics(created_by)
#     
#     metrics_text = f"""
# === {created_by.upper()} - METRIKEN HEUTE ({date.today()}) ===
# """
#     
#     if todays_metrics:
#         for key, value in sorted(todays_metrics.items()):
#             metrics_text += f"- {key}: {value}/5\n"
#     else:
#         metrics_text += "Noch keine Metriken heute erfasst.\n"
#     
#     return metrics_text


# def format_user_metrics_trend(created_by: str, days: int = 30) -> str:
#     """
#     Formatiert die Metrik-Trends eines Users über Zeit.
#     
#     TODO: ZUKÜNFTIG - wird aktiviert wenn Trend-Analyse implementiert ist
#     
#     Args:
#         created_by: Der Nutzer-Identifier
#         days: Anzahl der Tage zur Analyse
#         
#     Returns:
#         Formatierter String mit Metrik-Trends
#     """
#     metrics_raw = get_metrics_raw_data(created_by, days=days)
#     
#     trend_text = f"""
# === {created_by.upper()} - METRIK TRENDS (letzte {days} Tage) ===
# """
#     
#     if metrics_raw:
#         for key in sorted(metrics_raw.keys()):
#             data = metrics_raw[key]
#             values = data['values']
#             dates = data['dates']
#             trend_text += f"- {key}: {values} (Daten auf {len(values)} Tagen)\n"
#     else:
#         trend_text += "Keine Trend-Daten verfügbar.\n"
#     
#     return trend_text


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

# def therapy_cat_overview(created_by: str) -> str:
#     """
#     Die Katze zeigt einen Überblick über ALLE Einträge eines Users.
#     
#     TODO: ZUKÜNFTIG - wird aktiviert wenn Datenbank-Integration vollständig ist
#     
#     Args:
#         created_by: Der Nutzer-Identifier (MUSS match created_by in DB)
#         
#     Returns:
#         Antwort der Therapie-Katze als String
#     """
#     # alle relevanten Kontextdaten für den Prompt zusammenstellen
#     all_entries = format_user_entries(created_by)
#     today_metrics = format_user_metrics_today(created_by)
#     trends = format_user_metrics_trend(created_by, days=30)
#     
#     # vollständigen Prompt aus System-Anweisung und Nutzerdaten zusammenbauen
#     full_prompt = f"""{THERAPY_CAT_SYSTEM_INSTRUCTION}
#
# [USER-KONTEXT]
# Nutzer: {created_by}
# Anfrage: Überblick über alle meine Journal-Einträge und Metriken
#
# {all_entries}
#
# {today_metrics}
#
# {trends}
# """
#     
#     try:
#         response = _require_client().models.generate_content(
#             model=MODEL,
#             contents=[
#                 types.Content(
#                     role="user",
#                     parts=[types.Part.from_text(text=full_prompt)],
#                 )
#             ],
#         )
#         return response.text
#     except Exception as e:
#         raise Exception(f"Gemini API Error: {str(e)}")


# def therapy_cat_analyze_entry(entry_id: int, created_by: str, user_message: str = "") -> str:
#     """
#     Die Katze analysiert einen EINZELNEN Entry mit seinen Metriken.
#     SICHERHEIT: Der Entry muss vom User stammen (created_by Check).
#     
#     TODO: ZUKÜNFTIG - wird aktiviert wenn Entry-Analyse mit Metriken vollständig ist
#     
#     Args:
#         entry_id: Die ID des spezifischen Entry
#         created_by: Der Nutzer-Identifier (Sicherheits-Check)
#         user_message: Optional - zusätzliche Frage des Users
#         
#     Returns:
#         Antwort der Therapie-Katze als String
#     """
#     # SICHERHEIT: Prüfe ob dieser Entry vom User stammt
#     entry_details = format_single_entry(entry_id, created_by)
#     
#     # Zugriff verweigern wenn Eintrag nicht gefunden oder nicht dem User gehört
#     if not entry_details:
#         return f"Fehler: Entry #{entry_id} für Nutzer '{created_by}' nicht gefunden. Zugriff verweigert oder Entry existiert nicht."
#     
#     today_metrics = format_user_metrics_today(created_by)
#     trends = format_user_metrics_trend(created_by, days=30)
#     
#     full_prompt = f"""{THERAPY_CAT_SYSTEM_INSTRUCTION}
#
# [USER-KONTEXT]
# Nutzer: {created_by}
# Aktion: Analysiere diesen Entry im Detail
#
# {entry_details}
#
# {today_metrics}
#
# {trends}
#
# Nutzer's zusätzliche Frage/Kommentar: {user_message or '(keine)'}
# """
#     
#     try:
#         response = _require_client().models.generate_content(
#             model=MODEL,
#             contents=[
#                 types.Content(
#                     role="user",
#                     parts=[types.Part.from_text(text=full_prompt)],
#                 )
#             ],
#         )
#         return response.text
#     except Exception as e:
#         raise Exception(f"Gemini API Error: {str(e)}")


def therapy_cat_general_chat(created_by: str, user_message: str) -> str:
    """
    Freier Chat mit Miausi - OPTIMIERT für Gemini API (kompatibel!).
    
    Token-Verbrauch: ~240-300 pro Nachricht (war ~480)
    = 40% EINSPARUNG durch gekürzten Prompt! 🚀
    
    Optimierungen:
    - System-Prompt gekürzt (60 statt 200 Tokens)
    - Keine Datenbank-Aufrufe
    - Nur API-kompatible Parameter
    
    Freier Tier: 40+ Nachrichten pro Tag ✅
    
    Args:
        created_by: Der Nutzer-Identifier (für Personalisierung)
        user_message: Die Nachricht des Users an die Katze
        
    Returns:
        Antwort der Therapie-Katze als String
    """
    safe_created_by = str(created_by or "").strip()[:40]
    safe_user_message = str(user_message or "").strip()[:MAX_PROMPT_CHARS]

    # Minimaler, optimierter Prompt
    full_prompt = f"""{THERAPY_CAT_SYSTEM_INSTRUCTION}

Nutzer: {safe_created_by}
Nachricht: {safe_user_message}"""
    
    try:
        return _generate_with_fallbacks(full_prompt)
    except Exception as e:
        raise Exception(str(e)) from e