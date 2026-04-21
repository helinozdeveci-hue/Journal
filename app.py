#!/usr/bin/env python3
"""Journal App - GUI mit Therapy Cat KI Integration"""

from datetime import date, datetime
import customtkinter as ctk
from db import (
    create_entry, delete_entry, delete_entry_value, get_entry_with_values,
    init_db, list_entries, list_metrics, set_entry_value, update_entry,
)

# [21.04.2026] User-Management Import
from user_config import get_current_user, set_current_user, print_config_info

# KI-Integration mit Fallback
try:
    from test_gemini import therapy_cat_general_chat, therapy_cat_analyze_entry
    KI_AVAILABLE = True
except ImportError:
    KI_AVAILABLE = False
    def therapy_cat_general_chat(*args, **kwargs):
        return "KI nicht verfügbar. Installiere: pip install google-genai"
    def therapy_cat_analyze_entry(*args, **kwargs):
        return "KI nicht verfügbar. Installiere: pip install google-genai"

 


class JournalApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        init_db()
        
        # [21.04.2026] User-Management: Lade oder frage nach User
        self.current_user = get_current_user()
        if not self.current_user:
            self._show_login_dialog()
        else:
            print_config_info()  # [21.04.2026] Debug-Info
        
        if not self.current_user:
            # User hat Login abgebrochen
            self.destroy()
            return
        
        self.title("Journal App - Entries & Therapy Cat 🐱")
        self.geometry("900x620")
        self._maximize_window()
        self._build_ui()

    def _maximize_window(self) -> None:
        self.resizable(True, True)
        try:
            self.state("zoomed")
        except Exception:
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            self.geometry(f"{screen_w}x{screen_h}+0+0")

    # [21.04.2026] Login-Dialog beim ersten Start
    def _show_login_dialog(self) -> None:
        """Zeige Willkommens-Dialog für neuen User"""
        login_window = ctk.CTkToplevel(self)
        login_window.title("Willkommen!")
        login_window.geometry("400x200")
        login_window.resizable(False, False)
        
        # [21.04.2026] Center the window
        login_window.grab_set()
        login_window.focus()
        
        ctk.CTkLabel(
            login_window, 
            text="Wer bist du?",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(padx=20, pady=20)
        
        username_entry = ctk.CTkEntry(login_window, placeholder_text="Dein Name...")
        username_entry.pack(padx=20, pady=10, sticky="ew")
        
        def confirm_login():
            username = username_entry.get().strip()
            if username:
                self.current_user = username
                set_current_user(username)  # [21.04.2026] Speichere User
                print_config_info()  # [21.04.2026] Debug-Info
                login_window.destroy()
            else:
                ctk.CTkLabel(login_window, text="Bitte gib einen Namen ein!", text_color="red").pack()
        
        ctk.CTkButton(login_window, text="Bestätigen", command=confirm_login).pack(padx=20, pady=10, sticky="ew")
        
        # [21.04.2026] Focus und Enter-Key
        username_entry.focus()
        username_entry.bind("<Return>", lambda e: confirm_login())
        
        # Warte auf Bestätigung
        self.wait_window(login_window)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(header, text="Alle Entries", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, sticky="w")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")
        
        # [21.04.2026] User-Info Button mit Wechsel-Option
        ctk.CTkButton(btn_frame, text=f"👤 {self.current_user}", width=100, fg_color="#4A90E2",
                     command=self._open_user_switch).pack(side="left", padx=4)
        
        if KI_AVAILABLE:
            ctk.CTkButton(btn_frame, text="🐱 KI Katze", width=120, fg_color="#FF6B6B",
                         command=self._open_cat_chat).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="+ Eintrag", command=self._open_add_dialog).pack(side="left", padx=4)

        # Entry Liste
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=1, column=0, padx=16, pady=(8, 16), sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.entries_frame = ctk.CTkScrollableFrame(table_frame)
        self.entries_frame.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        self.entries_frame.grid_columnconfigure(0,weight=1)
        self._render_entries()

    def _render_entries(self) -> None:
        for w in self.entries_frame.winfo_children():
            w.destroy()
        entries = list_entries()
        if not entries:
            ctk.CTkLabel(self.entries_frame, text="Keine Entries vorhanden.").grid(row=0, column=0, padx=8, pady=8, sticky="w")
            return

        for idx, e in enumerate(entries):
            note = (e.get("note") or "").replace("\n", " ")[:50]
            author = e.get("created_by") or "-"
            row = ctk.CTkFrame(self.entries_frame, fg_color="transparent")
            row.grid(row=idx, column=0, padx=8, pady=6, sticky="ew")
            row.grid_columnconfigure(0, weight=1)

            card = ctk.CTkFrame(row, height=100)
            card.grid(row=0, column=0, sticky="ew")
            card.grid_columnconfigure(0, weight=1)
            card.grid_propagate(False)

            info = f"#{e['id']} | {e['date']} | {author}"
            ctk.CTkLabel(card, text=info, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")
            note_text = note + ("..." if len(note) > 45 else "")
            ctk.CTkLabel(card, text=f"Notiz: {note_text}").grid(row=1, column=0, padx=12, pady=(2, 8), sticky="w")

            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.grid(row=0, column=1, rowspan=2, padx=12, sticky="e")
            ctk.CTkButton(btns, text="✏️", width=32,
                         command=lambda eid=e['id']: self._open_detail(eid)).pack(side="left", padx=2)

    # [21.04.2026] User-Wechsel Dialog
    def _open_user_switch(self) -> None:
        """Zeige Dialog zum User-Wechsel"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("User wechseln")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=f"Aktueller User: {self.current_user}", 
                    font=ctk.CTkFont(weight="bold")).pack(padx=20, pady=20)
        
        ctk.CTkLabel(dialog, text="Neuer Benutzername:").pack(padx=20, pady=(10, 5))
        
        username_entry = ctk.CTkEntry(dialog, placeholder_text="Neuer Name...")
        username_entry.pack(padx=20, pady=5, sticky="ew")
        
        def switch_user():
            new_username = username_entry.get().strip()
            if new_username and new_username != self.current_user:
                self.current_user = new_username
                set_current_user(new_username)  # [21.04.2026] Speichere neuen User
                print_config_info()  # [21.04.2026] Debug-Info
                
                # [21.04.2026] Aktualisiere Header und neuladen
                dialog.destroy()
                self._render_entries()
                # [21.04.2026] Aktualisiere User-Button
                for widget in self.winfo_children():
                    if isinstance(widget, ctk.CTkFrame):
                        for child in widget.winfo_children():
                            if isinstance(child, ctk.CTkFrame):
                                for btn in child.winfo_children():
                                    if isinstance(btn, ctk.CTkButton) and "👤" in btn.cget("text"):
                                        btn.configure(text=f"👤 {self.current_user}")
        
        ctk.CTkButton(dialog, text="Wechseln", command=switch_user).pack(padx=20, pady=10, sticky="ew")
        
        username_entry.focus()
        username_entry.bind("<Return>", lambda e: switch_user())

    def _open_cat_chat(self) -> None:
        """Chat mit KI Katze"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Chat mit Miau 🐱")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog. grab_set()
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(dialog, text="Sprich mit deiner Therapy-Katze",
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=14, pady=14)

        chat_display = ctk.CTkTextbox(dialog, state="disabled")
        chat_display.grid(row=1, column=0, padx=14, sticky="nsew")

        input_frame = ctk.CTkFrame(dialog)
        input_frame.grid(row=2, column=0, padx=14, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        user_input = ctk.CTkTextbox(input_frame, height=70)
        user_input.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        status = ctk.CTkLabel(input_frame, text="")
        status.grid(row=1, column=0, sticky="w")

        def send():
            msg = user_input.get("1.0", "end").strip()
            if not msg:
                return
            user_input.configure(state="disabled")
            send_btn.configure(state="disabled")
            status.configure(text="Miau überlegt...", text_color="gray")
            dialog.update()

            try:
                response = therapy_cat_general_chat(created_by=self.current_user, user_message=msg)
                chat_display.configure(state="normal")
                chat_display.insert("end", f"\nDU:\n{msg}\n\nMIAU:\n{response}\n{'='*50}\n")
                chat_display.see("end")
                chat_display.configure(state="disabled")
                user_input.delete("1.0", "end")
                status.configure(text="✓ Nachricht gesendet", text_color="green")
            except Exception as ex:
                error_msg = str(ex)
                print(f"DEBUG - Chat Error: {error_msg}")  # Print to console for debugging
                status.configure(text=f"Fehler: {error_msg[:100]}", text_color="red")
                # Show full error in chat for visibility
                chat_display.configure(state="normal")
                chat_display.insert("end", f"\n❌ FEHLER:\n{error_msg}\n{'='*50}\n")
                chat_display.see("end")
                chat_display.configure(state="disabled")
            finally:
                user_input.configure(state="normal")
                send_btn.configure(state="normal")
                dialog.after(2000, lambda: status.configure(text=""))

        send_btn = ctk.CTkButton(input_frame, text="Senden", command=send, height=40)
        send_btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def _open_entry_chat(self, entry_id: int) -> None:
        """Chat über einen Entry"""
        entry = get_entry_with_values(entry_id)
        if not entry:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Chat über Entry #{entry_id}")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(2, weight=1)

        note_preview = (entry.get("note") or "")[:40]
        ctk.CTkLabel(dialog, text=f"{entry['date']} | {note_preview}...").grid(row=0, column=0, padx=14, pady=14)

        chat_display = ctk.CTkTextbox(dialog, state="disabled")
        chat_display.grid(row=1, column=0, padx=14, sticky="nsew")

        input_frame = ctk.CTkFrame(dialog)
        input_frame.grid(row=2, column=0, padx=14, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        user_input = ctk.CTkTextbox(input_frame, height=70)
        user_input.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        status = ctk.CTkLabel(input_frame, text="")
        status.grid(row=1, column=0, sticky="w")

        def send():
            msg = user_input.get("1.0", "end").strip()
            if not msg:
                return
            user_input.configure(state="disabled")
            send_btn.configure(state="disabled")
            status.configure(text="Miau analysiert...")
            dialog.update()

            try:
                response = therapy_cat_analyze_entry(entry_id=entry_id, created_by=self.current_user, user_message=msg)
                chat_display.configure(state="normal")
                chat_display.insert("end", f"\nDU:\n{msg}\n\nMIAU:\n{response}\n{'='*50}\n")
                chat_display.see("end")
                chat_display.configure(state="disabled")
                user_input.delete("1.0", "end")
            except Exception as ex:
                status.configure(text=f"Fehler: {str(ex)[:40]}", text_color="red")
            finally:
                user_input.configure(state="normal")
                send_btn.configure(state="normal")
                status.configure(text="")

        send_btn = ctk.CTkButton(input_frame, text="Senden", command=send, height=40)
        send_btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def _open_detail(self, entry_id: int) -> None:
        """Entry Details"""
        entry = get_entry_with_values(entry_id)
        if not entry:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Entry #{entry_id}")
        dialog.geometry("560x600")
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(3, weight=1)

        # Header
        header = ctk.CTkFrame(dialog, fg_color="transparent")
        header.grid(row=0, column=0, padx=14, pady=14, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(header, text=f"Entry #{entry['id']}", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=1, sticky="w")

        btns = ctk.CTkFrame(header, fg_color="transparent")
        btns.grid(row=0, column=2, sticky="e")
        ctk.CTkButton(btns, text="Bearbeiten", command=lambda: self._open_edit(dialog, entry_id)).pack(side="left", padx=2)
        ctk.CTkButton(btns, text="Löschen", fg_color="red", command=lambda: self._confirm_delete(dialog, entry_id)).pack(side="left", padx=2)

        # Info
        info_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        info_frame.grid(row=1, column=0, padx=14, pady=8, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(info_frame, text="Datum:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(info_frame, text=entry['date']).grid(row=0, column=1, sticky="w", padx=(8, 0))
        
        ctk.CTkLabel(info_frame, text="Von:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", pady=(4, 0))
        ctk.CTkLabel(info_frame, text=entry.get('created_by', '-')).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(4, 0))
        
        ctk.CTkLabel(info_frame, text="Notiz:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="nw", pady=(4, 0))
        ctk.CTkLabel(info_frame, text=entry.get('note', '-'), wraplength=350, justify="left").grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(4, 0))

        # Metriken Header
        ctk.CTkLabel(dialog, text="Metriken:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, padx=14, pady=(12, 8), sticky="w")

        # Metriken
        values_frame = ctk.CTkScrollableFrame(dialog)
        values_frame.grid(row=3, column=0, padx=14, pady=8, sticky="nsew")
        values_frame.grid_columnconfigure(0, weight=1)

        values = entry.get("values", [])
        if not values:
            ctk.CTkLabel(values_frame, text="Keine Metriken erfasst.").pack(anchor="w", padx=10, pady=10)
        else:
            for v in values:
                metric_text = f"{v['metric_key']}: {v['value']}/5"
                ctk.CTkLabel(values_frame, text=metric_text, text_color="#90EE90").pack(anchor="w", padx=10, pady=4)

    def _open_edit(self, parent: ctk.CTkToplevel, entry_id: int) -> None:
        """Entry bearbeiten"""
        entry = get_entry_with_values(entry_id)
        if not entry:
            return

        metrics = list_metrics()
        values = {v["metric_id"]: str(v["value"]) for v in entry.get("values", [])}
        vars = {}

        dialog = ctk.CTkToplevel(parent)
        dialog.title(f"Entry #{entry_id} bearbeiten")
        dialog.geometry("520x700")
        dialog.transient(parent)
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(dialog, text="Eintrag bearbeiten", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=14, pady=14, sticky="w")

        # Felder
        info = ctk.CTkFrame(dialog, fg_color="transparent")
        info.grid(row=1, column=0, padx=14, pady=8, sticky="ew")
        info.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(info, text="Datum", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
        date_entry = ctk.CTkEntry(info)
        date_entry.insert(0, entry["date"])
        date_entry.grid(row=0, column=1, padx=(8,0), sticky="ew")

        ctk.CTkLabel(info, text="Erstellt von", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", pady=4)
        author = ctk.CTkEntry(info)
        if entry.get("created_by"):
            author.insert(0, entry["created_by"])
        author.grid(row=1, column=1, padx=(8, 0), sticky="ew", pady=4)

        ctk.CTkLabel(info, text="Notiz", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="nw", pady=4)
        note_box = ctk.CTkTextbox(info, height=80)
        if entry.get("note"):
            note_box.insert("1.0", entry["note"])
        note_box.grid(row=2, column=1, padx=(8, 0), sticky="ew", pady=4)

        # Metriken Header
        ctk.CTkLabel(dialog, text="Metriken:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, padx=14, pady=(12, 8), sticky="w")

        # Metriken
        values_frame = ctk.CTkScrollableFrame(dialog)
        values_frame.grid(row=3, column=0, padx=14, pady=8, sticky="nsew")
        values_frame.grid_columnconfigure(1, weight=1)

        for row, m in enumerate(metrics):
            ctk.CTkLabel(values_frame, text=m["key"]).grid(row=row, column=0, padx=10, pady=4, sticky="w")
            default = values.get(m["id"], "-")
            var = ctk.StringVar(value=default)
            vars[m["id"]] = var
            ctk.CTkOptionMenu(values_frame, variable=var, values=["-", "1", "2", "3", "4", "5"]).grid(row=row, column=1, padx=10, pady=4, sticky="e")

        # Speichern
        def save():
            try:
                datetime.strptime(date_entry.get().strip(), "%Y-%m-%d")
            except ValueError:
                return

            author_val = author.get().strip() or self.current_user
            note_val = note_box.get("1.0", "end").strip() or None
            update_entry(entry_id, date=date_entry.get(), note=note_val, created_by=author_val)

            for mid, var in vars.items():
                if var.get() == "-":
                    delete_entry_value(entry_id, mid)
                else:
                    set_entry_value(entry_id, mid, int(var.get()))

            self._render_entries()
            dialog.destroy()
            parent.destroy()

        ctk.CTkButton(dialog, text="Speichern", command=save, height=40).grid(row=4, column=0, padx=14, pady=14, sticky="ew")

    def _open_add_dialog(self) -> None:
        """Neuen Entry anlegen"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neuen Entry anlegen")
        dialog.geometry("460x300")
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(dialog, text="Neuen Entry anlegen", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, padx=14, pady=14, sticky="w")

        ctk.CTkLabel(dialog, text="Datum").grid(row=1, column=0, padx=14, sticky="w")
        date_e = ctk.CTkEntry(dialog)
        date_e.insert(0, date.today().isoformat())
        date_e.grid(row=1, column=1, padx=14, sticky="ew")

        ctk.CTkLabel(dialog, text="Erstellt von").grid(row=2, column=0, padx=14, sticky="w", pady=4)
        author_e = ctk.CTkEntry(dialog)
        author_e.grid(row=2, column=1, padx=14, sticky="ew", pady=4)

        ctk.CTkLabel(dialog, text="Notiz").grid(row=3, column=0, padx=14, sticky="nw", pady=4)
        note_e = ctk.CTkTextbox(dialog, height=100)
        note_e.grid(row=3, column=1, padx=14, sticky="ew", pady=4)

        status = ctk.CTkLabel(dialog, text="")
        status.grid(row=4, column=0, columnspan=2, padx=14, sticky="w")

        def next_step():
            date_text = date_e.get().strip()
            try:
                datetime.strptime(date_text, "%Y-%m-%d")
            except ValueError:
                status.configure(text="Ungültiges Datum!", text_color="red")
                return
            author_val = author_e.get().strip() or self.current_user
            note_val = note_e.get("1.0", "end").strip() or None
            dialog.destroy()
            self._open_metrics_dialog(date_text, author_val, note_val)

        ctk.CTkButton(dialog, text="Weiter", command=next_step, height=40).grid(row=5, column=0, columnspan=2, padx=14, pady=10, sticky="ew")

    def _open_metrics_dialog(self, date_text: str, author: str | None, note: str | None) -> None:
        """Metriken für neuenEntry"""
        metrics = list_metrics()
        vars = {}

        dialog = ctk.CTkToplevel(self)
        dialog.title("Metriken und Werte")
        dialog.geometry("520x500")
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(dialog, text=f"Datum: {date_text}", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=14, pady=14, sticky="w")

        values_frame = ctk.CTkScrollableFrame(dialog)
        values_frame.grid(row=1, column=0, padx=14, pady=8, sticky="nsew")
        values_frame.grid_columnconfigure(0, weight=1)

        for row, m in enumerate(metrics):
            ctk.CTkLabel(values_frame, text=m["key"]).grid(row=row, column=0, padx=10, pady=4, sticky="w")
            var = ctk.StringVar(value="-")
            vars[m["id"]] = var
            ctk.CTkOptionMenu(values_frame, variable=var, values=["-", "1", "2", "3", "4", "5"]).grid(row=row, column=1, padx=10, pady=4, sticky="e")

        status = ctk.CTkLabel(dialog, text="")
        status.grid(row=2, column=0, padx=14, pady=8, sticky="w")

        def save():
            selected = [mid for mid, v in vars.items() if v.get() != "-"]
            if not selected:
                status.configure(text="Mindestens eine Metrik erforderlich!", text_color="red")
                return

            eid = create_entry(date_text, note=note, created_by=author)
            for mid in selected:
                set_entry_value(eid, mid, int(vars[mid].get()))

            self._render_entries()
            status.configure(text=f"Entry #{eid} gespeichert!", text_color="green")
            dialog.after(500, dialog.destroy)

        ctk.CTkButton(dialog, text="Speichern", command=save, height=40).grid(row=3, column=0, padx=14, pady=10, sticky="ew")

    def _confirm_delete(self, parent: ctk.CTkToplevel, entry_id: int) -> None:
        """Löschen bestätigen"""
        confirm = ctk.CTkToplevel(parent)
        confirm.title("Bestätigung")
        confirm.geometry("350x120")
        confirm.transient(parent)
        confirm.grab_set()

        ctk.CTkLabel(confirm, text=f"Entry #{entry_id} löschen?").pack(padx=14, pady=14)

        btns = ctk.CTkFrame(confirm, fg_color="transparent")
        btns.pack(padx=14, pady=10, fill="x")

        def do_delete():
            delete_entry(entry_id)
            self._render_entries()
            confirm.destroy()
            parent.destroy()

        ctk.CTkButton(btns, text="Abbrechen", command=confirm.destroy).pack(side="left", expand=True, fill="x", padx=2)
        ctk.CTkButton(btns, text="Löschen", fg_color="red", command=do_delete).pack(side="left", expand=True, fill="x", padx=2)


# [21.04.2026] - Entry Point der Anwendung mit User-Authentification
if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = JournalApp()  # [21.04.2026] - Startet __init__, zeigt Login-Dialog wenn nötig
    app.mainloop()