"""
Interaktives CLI-Interface für die Therapy Cat
Hier können Sie mit der KI interagieren und Ihre Einträge verwalten.
"""

from db import (
    create_entry, add_entry_value, get_user_entries, get_entry_with_metrics,
    get_user_todays_metrics, list_users, list_metrics, create_metric
)
from datetime import date
import sqlite3

# Importiere Therapy Cat Funktionen - aber mit Fallback wenn genai nicht verfügbar
try:
    from test_gemini import (
        therapy_cat_overview, therapy_cat_analyze_entry, therapy_cat_general_chat
    )
    GENAI_AVAILABLE = True
except ImportError:
    print("Warnung: google-genai nicht verfügbar. Chat-Funktionen deaktiviert.")
    GENAI_AVAILABLE = False
    
    # Dummy-Funktionen
    def therapy_cat_overview(*args, **kwargs):
        return "Entschuldigung, Miausi kann derzeit nicht sprechen (API nicht verfügbar). Bitte installiere: pip install google-genai"
    
    def therapy_cat_analyze_entry(*args, **kwargs):
        return "Entschuldigung, Miausi kann derzeit nicht sprechen (API nicht verfügbar). Bitte installiere: pip install google-genai"
    
    def therapy_cat_general_chat(*args, **kwargs):
        return "Entschuldigung, Miausi kann derzeit nicht sprechen (API nicht verfügbar). Bitte installiere: pip install google-genai"


class TherapyCatInterface:
    def __init__(self):
        self.current_user = None
        self.current_entry_id = None
        self.metrics_list = list_metrics()
        self.users = list_users()

    def clear_screen(self):
        """Bildschirm leeren (Windows & Unix)"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    # ===== BENUTZER-MANAGEMENT =====
    
    def select_or_create_user(self):
        """Benutzer auswählen oder neuen erstellen"""
        self.clear_screen()
        print("=" * 70)
        print("THERAPY CAT - Journal Assistant")
        print("=" * 70)
        
        if not self.users:
            print("\nKeine Benutzer gefunden. Bitte neuen Benutzer erstellen.\n")
            return self.create_new_user()
        
        print("\nBERÜHRTE BENUTZER IN DER DB:")
        for i, user in enumerate(self.users, 1):
            print(f"  {i}. {user}")
        
        print(f"\n  {len(self.users) + 1}. Neuer Benutzer")
        print("  0. Beenden")
        
        try:
            choice = int(input("\nWahl: "))
            
            if choice == 0:
                print("Auf Wiedersehen!")
                return False
            elif choice == len(self.users) + 1:
                return self.create_new_user()
            elif 1 <= choice <= len(self.users):
                self.current_user = self.users[choice - 1]
                print(f"\nBenutzer '{self.current_user}' ausgewählt!")
                input("Weiter mit Enter...")
                return True
            else:
                print("Ungültige Wahl!")
                input("Weiter mit Enter...")
                return self.select_or_create_user()
        except ValueError:
            print("Ungültige Eingabe!")
            input("Weiter mit Enter...")
            return self.select_or_create_user()

    def create_new_user(self):
        """Neuen Benutzer erstellen"""
        self.clear_screen()
        print("=" * 70)
        print("NEUEN BENUTZER ERSTELLEN")
        print("=" * 70)
        
        username = input("\nBenutzername: ").strip()
        if not username:
            print("Benutzername darf nicht leer sein!")
            input("Weiter mit Enter...")
            return self.create_new_user()
        
        self.current_user = username
        self.users.append(username)
        print(f"\nBenutzer '{username}' erstellt!")
        input("Weiter mit Enter...")
        return True

    # ===== ENTRY-MANAGEMENT =====
    
    def show_entries_menu(self):
        """Zeigt Menü für Entry-Verwaltung"""
        while True:
            self.clear_screen()
            print("=" * 70)
            print(f"EINTRÄGE - Benutzer: {self.current_user}")
            print("=" * 70)
            
            entries = get_user_entries(self.current_user)
            
            if not entries:
                print("\nKeine Einträge gefunden.\n")
            else:
                print(f"\n{len(entries)} Einträge gefunden:\n")
                for i, entry in enumerate(entries, 1):
                    metrics_str = f" ({len(entry['metrics'])} Metriken)" if entry['metrics'] else " (keine Metriken)"
                    print(f"  {i}. {entry['date']} - {entry['note'][:40] if entry['note'] else '(keine Notiz)'}{metrics_str}")
            
            print("\nOPTIONEN:")
            print("  1. Eintrag auswählen")
            print("  2. Neuen Eintrag erstellen")
            print("  3. Mit Katze chatten (allgemein)")
            print("  4. Überblick von Katze")
            print("  0. Zurück")
            
            choice = input("\nWahl: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                if entries:
                    self.select_entry(entries)
            elif choice == "2":
                self.create_new_entry()
            elif choice == "3":
                self.chat_with_cat_general()
            elif choice == "4":
                self.show_cat_overview()
            else:
                print("Ungültige Wahl!")
                input("Weiter mit Enter...")

    def select_entry(self, entries):
        """Eintrag auswählen"""
        self.clear_screen()
        print("=" * 70)
        print("EINTRAG AUSWÄHLEN")
        print("=" * 70 + "\n")
        
        for i, entry in enumerate(entries, 1):
            print(f"{i}. {entry['date']}")
        
        print("0. Zurück")
        
        try:
            choice = int(input("\nWahl: "))
            if choice == 0:
                return
            elif 1 <= choice <= len(entries):
                self.current_entry_id = entries[choice - 1]['entry_id']
                self.show_entry_detail()
            else:
                print("Ungültige Wahl!")
                input("Weiter mit Enter...")
        except ValueError:
            print("Ungültige Eingabe!")
            input("Weiter mit Enter...")

    def show_entry_detail(self):
        """Zeigt Details eines Eintrags"""
        while True:
            self.clear_screen()
            print("=" * 70)
            print(f"EINTRAG DETAIL - ID: {self.current_entry_id}")
            print("=" * 70)
            
            entry = get_entry_with_metrics(self.current_entry_id, created_by=self.current_user)
            
            if not entry:
                print("\nEintrag nicht gefunden oder kein Zugriff!")
                input("Weiter mit Enter...")
                return
            
            print(f"\nDatum: {entry['date']}")
            print(f"Notiz: {entry['note'] or '(keine Notiz)'}")
            print(f"\nMETRIKEN ({len(entry['metrics'])} erfasst):")
            
            if entry['metrics']:
                for key, value in sorted(entry['metrics'].items()):
                    print(f"  {key}: {value}/5")
            else:
                print("  (keine Metriken)")
            
            print("\nOPTIONEN:")
            print("  1. Mit Katze über diesen Eintrag chatten")
            print("  2. Metrik hinzufügen/ändern")
            print("  0. Zurück")
            
            choice = input("\nWahl: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.chat_about_entry()
            elif choice == "2":
                self.add_or_update_metric()
            else:
                print("Ungültige Wahl!")
                input("Weiter mit Enter...")

    def create_new_entry(self):
        """Neuen Eintrag erstellen"""
        self.clear_screen()
        print("=" * 70)
        print("NEUEN EINTRAG ERSTELLEN")
        print("=" * 70)
        
        entry_date = input(f"\nDatum (Standard: {date.today()}): ").strip()
        if not entry_date:
            entry_date = str(date.today())
        
        note = input("Notiz (Optional): ").strip()
        
        try:
            entry_id = create_entry(date=entry_date, note=note or None, created_by=self.current_user)
            print(f"\nEintrag #{entry_id} erstellt!")
            self.current_entry_id = entry_id
            
            # Metriken hinzufügen?
            add_metrics = input("\nMöchtest du Metriken hinzufügen? (j/n): ").strip().lower()
            if add_metrics == "j":
                self.add_or_update_metric()
            
            input("Weiter mit Enter...")
        except Exception as e:
            print(f"Fehler: {e}")
            input("Weiter mit Enter...")

    # ===== METRIKEN-MANAGEMENT =====
    
    def add_or_update_metric(self):
        """Metrik zu Eintrag hinzufügen oder aktualisieren"""
        self.clear_screen()
        print("=" * 70)
        print("METRIK HINZUFÜGEN/ÄNDERN")
        print("=" * 70 + "\n")
        
        print("VERFÜGBARE METRIKEN:\n")
        for i, metric in enumerate(self.metrics_list, 1):
            print(f"  {i}. {metric['key']}")
        
        print("  0. Zurück")
        
        try:
            choice = int(input("\nMetrik wählen: "))
            
            if choice == 0:
                return
            elif 1 <= choice <= len(self.metrics_list):
                metric_id = self.metrics_list[choice - 1]['id']
                metric_key = self.metrics_list[choice - 1]['key']
                
                print(f"\nMetrik: {metric_key}")
                print("Wert eingeben (1-5):")
                
                try:
                    value = int(input("Wert: "))
                    
                    if 1 <= value <= 5:
                        add_entry_value(self.current_entry_id, metric_id, value)
                        print(f"Metrik '{metric_key}' = {value}/5 gespeichert!")
                        input("Weiter mit Enter...")
                    else:
                        print("Wert muss zwischen 1 und 5 liegen!")
                        input("Weiter mit Enter...")
                except ValueError:
                    print("Ungültige Eingabe!")
                    input("Weiter mit Enter...")
            else:
                print("Ungültige Wahl!")
                input("Weiter mit Enter...")
        except ValueError:
            print("Ungültige Eingabe!")
            input("Weiter mit Enter...")

    # ===== CHAT MIT KATZE =====
    
    def chat_with_cat_general(self):
        """Freier Chat mit der Katze"""
        self.clear_screen()
        print("=" * 70)
        print("CHAT MIT MIAUSI - Therapie-Katze")
        print("=" * 70)
        
        message = input("\nWas möchtest du der Katze sagen?\n(Oder 'quit' zum Beenden)\n\n>>> ").strip()
        
        if message.lower() == "quit":
            return
        
        if not message:
            print("Bitte eine Nachricht eingeben!")
            input("Weiter mit Enter...")
            return
        
        print("\nMiausi überlegt...\n")
        
        try:
            response = therapy_cat_general_chat(
                created_by=self.current_user,
                user_message=message
            )
            
            self.clear_screen()
            print("=" * 70)
            print("MIAUSI ANTWORTET:")
            print("=" * 70)
            print(f"\n{response}\n")
            input("Weiter mit Enter...")
        except Exception as e:
            print(f"Fehler beim Chatten: {e}")
            input("Weiter mit Enter...")

    def chat_about_entry(self):
        """Chat über einen spezifischen Eintrag"""
        self.clear_screen()
        print("=" * 70)
        print(f"CHAT ÜBER EINTRAG #{self.current_entry_id}")
        print("=" * 70)
        
        message = input("\nWas möchtest du über diesen Eintrag wissen?\n(Oder 'quit' zum Beenden)\n\n>>> ").strip()
        
        if message.lower() == "quit":
            return
        
        if not message:
            print("Bitte eine Frage eingeben!")
            input("Weiter mit Enter...")
            return
        
        print("\nMiausi analysiert diesen Eintrag...\n")
        
        try:
            response = therapy_cat_analyze_entry(
                entry_id=self.current_entry_id,
                created_by=self.current_user,
                user_message=message
            )
            
            self.clear_screen()
            print("=" * 70)
            print("MIAUSI ANTWORTET:")
            print("=" * 70)
            print(f"\n{response}\n")
            input("Weiter mit Enter...")
        except Exception as e:
            print(f"Fehler: {e}")
            input("Weiter mit Enter...")

    def show_cat_overview(self):
        """Zeigt Überblick von der Katze"""
        self.clear_screen()
        print("=" * 70)
        print("MIAUSI ANALYSIERT DEINE EINTRÄGE...")
        print("=" * 70)
        print("\nEine Moment, deine Katze überlegt...\n")
        
        try:
            response = therapy_cat_overview(created_by=self.current_user)
            
            self.clear_screen()
            print("=" * 70)
            print("MIAUSI ÜBERBLICK:")
            print("=" * 70)
            print(f"\n{response}\n")
            input("Weiter mit Enter...")
        except Exception as e:
            print(f"Fehler: {e}")
            input("Weiter mit Enter...")

    # ===== HAUPTMENÜ =====
    
    def run(self):
        """Starten Sie das Interface"""
        while True:
            # Benutzer auswählen
            if not self.select_or_create_user():
                break
            
            # Hauptmenü
            self.show_entries_menu()


def main():
    """Einstiegspunkt"""
    interface = TherapyCatInterface()
    interface.run()


# ===== TEST DATEN ERSTELLEN (optional) =====

def create_test_data():
    """Erstellt Test-Daten zum Ausprobieren"""
    print("Erstelle Test-Daten...\n")
    
    from db import init_db
    init_db()
    
    # Test-User und Entries
    test_user = "TestUser"
    
    try:
        # Eintrag 1
        entry1_id = create_entry(
            date="2026-04-14",
            note="War ein stressiger Tag heute, aber ich habe es geschafft!",
            created_by=test_user
        )
        add_entry_value(entry1_id, 1, 4)  # stomach ache
        add_entry_value(entry1_id, 2, 3)  # sad
        add_entry_value(entry1_id, 3, 4)  # stress
        add_entry_value(entry1_id, 4, 2)  # calm
        add_entry_value(entry1_id, 5, 2)  # energy
        
        # Eintrag 2
        entry2_id = create_entry(
            date="2026-04-15",
            note="Besserer Tag! Mit Freunden geredet und aktiv gewesen.",
            created_by=test_user
        )
        add_entry_value(entry2_id, 1, 1)  # stomach ache
        add_entry_value(entry2_id, 2, 1)  # sad
        add_entry_value(entry2_id, 3, 2)  # stress
        add_entry_value(entry2_id, 4, 4)  # calm
        add_entry_value(entry2_id, 5, 4)  # energy
        add_entry_value(entry2_id, 6, 5)  # happy
        
        # Eintrag 3 (heute)
        entry3_id = create_entry(
            date=str(date.today()),
            note="Heute ist produktiv Tag, fühle mich motiviert!",
            created_by=test_user
        )
        add_entry_value(entry3_id, 3, 1)  # stress (niedrig)
        add_entry_value(entry3_id, 4, 5)  # calm (hoch)
        add_entry_value(entry3_id, 5, 5)  # energy (hoch)
        add_entry_value(entry3_id, 6, 5)  # happy
        add_entry_value(entry3_id, 8, 1)  # anxious
        
        print(f"OK! 3 Test-Einträge für '{test_user}' erstellt!")
        print(f"  - Entry 1 (2026-04-14): 5 Metriken")
        print(f"  - Entry 2 (2026-04-15): 6 Metriken")
        print(f"  - Entry 3 (heute): 5 Metriken")
        print(f"\nStarten Sie 'python chat_interface.py' um zu chatten!\n")
    except sqlite3.IntegrityError as e:
        print(f"Test-Daten existieren schon: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create-test-data":
        create_test_data()
    else:
        main()
