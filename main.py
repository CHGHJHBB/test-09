from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

# --- Config Telegram ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Fichier local pour stocker les anciens ELO ---
LAST_ELO_FILE = "last_elo.json"

# Charger les ELO sauvegardés
def load_last_elo():
    try:
        with open(LAST_ELO_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Sauvegarder les ELO
def save_last_elo(data):
    with open(LAST_ELO_FILE, "w") as f:
        json.dump(data, f)

# Envoyer un message Telegram
def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )

# --- Route "ping" pour Render / UptimeRobot ---
@app.route("/", methods=["GET", "HEAD"])
def home():
    return "OK", 200

# --- Route de test pour Telegram ---
@app.route("/test", methods=["GET", "HEAD"])
def test_message():
    if request.method == "HEAD":
        return "", 200
    send_telegram("🧪 Test : la connexion Telegram fonctionne !")
    return "Message test envoyé !", 200

# --- Exemple de vérification d’ELO ---
@app.route("/check", methods=["GET", "HEAD"])
def check_elo():
    if request.method == "HEAD":
        return "", 200

    # Exemple de données (à remplacer par ton API réelle)
    players = [
        {"username": "Alice", "elo": 1200},
        {"username": "Bob", "elo": 1250},
    ]

    last_elo = load_last_elo()

    for p in players:
        username = p["username"]
        elo = p["elo"]

        if username not in last_elo or last_elo[username] != elo:
            send_telegram(f"{username} a maintenant {elo} ELO !")
            last_elo[username] = elo

    save_last_elo(last_elo)

    return "Check ELO done", 200


# --- Lancement ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
