import tkinter as tk
from tkinter import messagebox

import webbrowser
from user_key_config import load_key, save_key

def key_popup(callback):
    existing_key = load_key()
    if existing_key:
        callback(existing_key)
        return
    fenster = tk.Toplevel()
    fenster.title("API Key erforderlich")
    fenster.geometry("420x430")
    fenster.resizable(False, False)

    tk.Label(fenster, text="Google API Key erforderlich", font=("Arial", 13, "bold")).pack(pady=(20, 5))

    tk.Label(fenster, text="Um die KI-Funktion zu nutzen, brauchst du einen\n"
                           "kostenlosen Google API Key.", justify="center").pack()
    tk.Label(fenster, text="Der Key wird nur lokal auf diesem Rechner gespeichert\n"
                           "und nicht mit der EXE verteilt.", justify="center").pack()
    tk.Label(fenster, text="Freunde bekommen keinen gemeinsamen Key und\n"
                           "keinen Zugriff auf deine lokale Datenbank.", justify="center").pack()
    tk.Label(fenster, text="Bei Get API Key.\n"
                           "API Schlüssel erstellen", justify="center").pack()

    link = tk.Label(fenster, text="→ Hier Key kostenlos erstellen",
                    fg="blue", cursor="hand2")
    link.pack(pady=5)
    link.bind("<Button-1>", lambda e: webbrowser.open("https://aistudio.google.com/api-keys"))

    tk.Label(fenster, text="Key hier einfügen:").pack()
    eingabe = tk.Entry(fenster, width=45, show="*")
    eingabe.pack(pady=5)

    def save_key_and_start():
        key = eingabe.get().strip()
        if not key:
            messagebox.showwarning("Fehlt", "Kein API-Key eingegeben! Bitte eingeben :)")
            return
        save_key(key)
        fenster.destroy()
        callback(key)