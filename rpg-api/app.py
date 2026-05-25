from flask import Flask, jsonify, request
import csv

app = Flask(__name__)

def charger_monstres():
    monstres = []
    with open("monsters.csv", "r") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne:
                continue
            champs = ligne.split(";")
            if len(champs) >= 6:
                monstres.append({
                    "categorie": champs[0],
                    "nom": champs[1],
                    "hp": champs[2],
                    "atk": champs[3],
                    "def": champs[4],
                    "mercy": champs[5]
                })
    return monstres

@app.route("/monstres", methods=["GET"])
def get_monstres():
    return jsonify(charger_monstres())

@app.route("/monstres/<nom>", methods=["GET"])
def get_monstre(nom):
    for m in charger_monstres():
        if m["nom"].lower() == nom.lower():
            return jsonify(m)
    return jsonify({"erreur": "Monstre introuvable"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)