import os
import sys
from dotenv import load_dotenv

# Load .env only for development (when not running a frozen executable)
if not getattr(sys, "frozen", False):
    load_dotenv()

# Store user API key in a per-user AppData folder to avoid bundling a developer
# key inside the distributable EXE. This prevents your personal key from being
# shipped to friends.
APP_DIR = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "JournalTherapyCat")
KEY_DATA = os.path.join(APP_DIR, "api_key.txt")

def _ensure_appdir():
    try:
        os.makedirs(APP_DIR, exist_ok=True)
    except Exception:
        # If creation fails, fall back to current directory (best-effort)
        return APP_DIR
    return APP_DIR


def get_app_dir():
    return _ensure_appdir()


# Ensure the directory exists immediately when the module is imported.
get_app_dir()

def load_key():
    """
    Load API key with the following priority:
    1. Environment variable `GEMINI_API_KEY` (useful for dev/testing)
    2. Per-user key stored in `%APPDATA%\JournalTherapyCat\api_key.txt`
    Returns None if no key is found.
    """
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # Check per-user storage
    try:
        if os.path.exists(KEY_DATA):
            with open(KEY_DATA, "r", encoding="utf-8") as f:
                key = f.read().strip()
                if key:
                    return key
    except Exception:
        # Ignore read errors and behave as if no key is present
        pass

    return None

def save_key(key):
    """Save the given API key to the per-user AppData path."""
    get_app_dir()
    with open(KEY_DATA, "w", encoding="utf-8") as f:
        f.write(key)
