from flask import Flask, jsonify, request, render_template
import os
import sqlite3
import jwt
import datetime

app = Flask(__name__)

TOKEN_SECRET = os.environ.get("API_SECRET_KEY", "changeme")
ADMIN_USER = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "password")
DATABASE = "database.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_existe = os.path.exists(DATABASE)
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS monstres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categorie TEXT,
            nom TEXT,
            hp TEXT,
            atk TEXT,
            def TEXT,
            mercy TEXT
        )
    """)
    conn.commit()

    if not db_existe:
        with open("monsters.csv", "r") as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne:
                    continue
                champs = ligne.split(";")
                if len(champs) >= 6:
                    conn.execute(
                        "INSERT INTO monstres (categorie, nom, hp, atk, def, mercy) VALUES (?, ?, ?, ?, ?, ?)",
                        (champs[0], champs[1], champs[2], champs[3], champs[4], champs[5])
                    )
        conn.commit()
    conn.close()

def verifier_token():
    auth = request.headers.get("Authorization")
    if not auth:
        return False
    if not auth.startswith("Bearer "):
        return False
    token = auth.split(" ")[1]
    try:
        jwt.decode(token, TOKEN_SECRET, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data:
        return jsonify({"erreur": "Donnees manquantes"}), 400

    username = data.get("username")
    password = data.get("password")

    if username != ADMIN_USER or password != ADMIN_PASSWORD:
        return jsonify({"erreur": "Identifiants incorrects"}), 401

    token = jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        },
        TOKEN_SECRET,
        algorithm="HS256"
    )

    return jsonify({"token": token})

@app.route("/monstres", methods=["GET"])
def get_monstres():
    conn = get_db()
    monstres = conn.execute("SELECT * FROM monstres").fetchall()
    conn.close()
    resultat = []
    for m in monstres:
        resultat.append(dict(m))
    return jsonify(resultat)

@app.route("/monstres/<nom>", methods=["GET"])
def get_monstre(nom):
    conn = get_db()
    monstre = conn.execute("SELECT * FROM monstres WHERE LOWER(nom) = LOWER(?)", (nom,)).fetchone()
    conn.close()
    if monstre is None:
        return jsonify({"erreur": "Monstre introuvable"}), 404
    return jsonify(dict(monstre))

@app.route("/monstres", methods=["POST"])
def ajouter_monstre():
    if not verifier_token():
        return jsonify({"erreur": "Non autorise"}), 401
    data = request.json
    conn = get_db()

    existant = conn.execute("SELECT * FROM monstres WHERE LOWER(nom) = LOWER(?)", (data["nom"],)).fetchone()
    if existant:
        conn.close()
        return jsonify({"erreur": f"{data['nom']} existe deja"}), 409

    conn.execute(
        "INSERT INTO monstres (categorie, nom, hp, atk, def, mercy) VALUES (?, ?, ?, ?, ?, ?)",
        (data["categorie"], data["nom"], data["hp"], data["atk"], data["def"], data["mercy"])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": f"{data['nom']} ajoute"}), 201

@app.route("/monstres/<nom>", methods=["DELETE"])
def supprimer_monstre(nom):
    if not verifier_token():
        return jsonify({"erreur": "Non autorise"}), 401
    conn = get_db()
    resultat = conn.execute("DELETE FROM monstres WHERE LOWER(nom) = LOWER(?)", (nom,)).rowcount
    conn.commit()
    conn.close()
    if resultat == 0:
        return jsonify({"erreur": "Monstre introuvable"}), 404
    return jsonify({"message": f"{nom} supprime"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)