import os
import requests
import psycopg2
from flask import Flask, request

app = Flask(__name__)

# --- Variables d’environnement ---
DATABASE_URL = os.getenv("DATABASE_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

API_URL = "https://api.worldguessr.com/api/leaderboard"


# --- Récupération des données depuis l’API ---
def get_data():
    resp = requests.get(API_URL)
    resp.raise_for_status()
    return resp.json().get("leaderboard", [])


# --- Comparaison en base ---
def compare_and_update(players):
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cur = conn.cursor()

    # création de table si n’existe pas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            username TEXT PRIMARY KEY,
            elo INTEGER
        )
    """)
    conn.commit()

    for p in players:
        name = p["username"]
        elo = p["elo"]

        # On ignore les joueurs < 8000
        if elo < 8000:
            continue

        cur.execute("SELECT elo FROM players WHERE username = %s", (name,))
        row = cur.fetchone()

        if row is None:
            # nouveau joueur
            cur.execute("INSERT INTO players (username, elo) VALUES (%s, %s)", (name, elo))
            conn.commit()
            msg = f"🆕 Nouveau joueur >8000 ELO : {name} ({elo})"
            send_telegram(msg)

        else:
            old_elo = row[0]
            if old_elo != elo:
                # changement d’ELO
                cur.execute("UPDATE players SET elo = %s WHERE username = %s", (elo, name))
                conn.commit()

                msg = f"🔔 {name} a changé d’ELO : {old_elo} → {elo}"
                send_telegram(msg)

    cur.close()
    conn.close()


# --- Envoi Telegram ---
def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text}
    )


# --- Route UptimeRobot (avec HEAD supporté) ---
@app.route("/", methods=["GET", "HEAD"])
def home():
    if request.method == "HEAD":
        return "", 200
    return "✅ WorldGuessr Tracker is running!", 200


# --- Route check (ping par UptimeRobot toutes les 5 min) ---
@app.route("/check", methods=["GET", "HEAD"])
def check():
    if request.method == "HEAD":
        return "", 200
    compare_and_update(get_data())
    return "✅ Check executed", 200


# --- Lancement serveur ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
