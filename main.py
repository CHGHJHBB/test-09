import os
import json
import requests
from flask import Flask

app = Flask(__name__)

# --- CONFIG ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LAST_ELO_FILE = "last_elo.json"


# --- Fonction d'envoi Telegram avec debug ---
def send_telegram(msg):
    print("Envoi Telegram :", msg)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    })

    print("Réponse Telegram :", r.status_code, r.text)  # <-- DEBUG IMPORTANT !

    return r.status_code


# --- Endpoint test ---
@app.route("/test")
def test():
    status = send_telegram("🔧 Test : le bot Telegram fonctionne !")
    return f"Test envoyé avec status {status}", 200


# --- Charger JSON ---
def load_data():
    try:
        with open(LAST_ELO_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# --- Sauvegarder JSON ---
def save_data(data):
    with open(LAST_ELO_FILE, "w") as f:
        json.dump(data, f)


# --- Récup API ---
def get_data():
    r = requests.get("https://api.worldguessr.com/api/leaderboard")
    r.raise_for_status()
    return r.json().get("leaderboard", [])


# --- Comparaison ---
def compare_and_update():
    last = load_data()
    new_data = get_data()

    for p in new_data:
        name = p["username"]
        elo = p["elo"]

        if elo < 8000:
            continue

        if name not in last or last[name] != elo:
            send_telegram(f"🔔 {name} → {elo} ELO")
            last[name] = elo

    save_data(last)


# --- Endpoint check ---
@app.route("/check")
def check():
    compare_and_update()
    return "Check effectué", 200


# --- Accueil / Uptime Robot ---
@app.route("/", methods=["GET", "HEAD"])
def home():
    return "OK", 200


# --- RUN ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
