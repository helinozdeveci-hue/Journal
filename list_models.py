from google import genai
from user_key_config import load_key

key = load_key()
client = genai.Client(api_key=key)

print("Verfügbare Modelle mit generateContent-Unterstützung:\n")
for m in client.models.list():
    actions = getattr(m, "supported_actions", None) or getattr(m, "supported_generation_methods", None) or []
    if "generateContent" in actions:
        print(m.name)