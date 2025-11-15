import json
import requests

# Config Telegram
TOKEN = "TON_BOT_TOKEN_ICI"
CHAT_ID = "TON_CHAT_ID_ICI"

# Fichier local pour stocker les derniers ELO
LAST_ELO_FILE = "last_elo.json"

# Charger les derniers ELO depuis le fichier
try:
    with open(LAST_ELO_FILE, "r") as f:
        last_elo = json.load(f)
except FileNotFoundError:
    last_elo = {}

# --- Récupération des joueurs depuis ton API ---
# Remplace cette partie par ton appel réel à l'API ou DB
# Exemple fictif :
players = [
    {"username": "Alice", "elo": 1200},
    {"username": "Bob", "elo": 1250},
]

# Comparer les ELO et notifier Telegram si changement
for player in players:
    username = player["username"]
    elo = player["elo"]

    if username not in last_elo or last_elo[username] != elo:
        # Envoyer message Telegram
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": f"{username} a maintenant {elo} ELO !"
        })
        # Mettre à jour le fichier
        last_elo[username] = elo

# Sauvegarder les ELO pour la prochaine vérification
with open(LAST_ELO_FILE, "w") as f:
    json.dump(last_elo, f)
