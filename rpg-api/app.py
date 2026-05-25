from flask import Flask, jsonify, request
import os

app = Flask(__name__)

TOKEN_SECRET = os.environ.get("API_SECRET_KEY", "changeme")

def verifier_token():
    token = request.headers.get("Authorization")
    if not token:
        return False
    if token != f"Bearer {TOKEN_SECRET}":
        return False
    return True

def charger_monstres():
    monstres = []
    with open("monsters.csv", "r") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne:
                continue
            champs = ligne.split(";")
            if len(champs) >= 6:
                monstre = {
                    "categorie": champs[0],
                    "nom": champs[1],
                    "hp": champs[2],
                    "atk": champs[3],
                    "def": champs[4],
                    "mercy": champs[5]
                }
                monstres.append(monstre)
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

@app.route("/monstres", methods=["POST"])
def ajouter_monstre():
    if not verifier_token():
        return jsonify({"erreur": "Non autorisé"}), 401
    
    data = request.json
    with open("monsters.csv", "a") as f:
        ligne = f"\n{data['categorie']};{data['nom']};{data['hp']};{data['atk']};{data['def']};{data['mercy']}"
        f.write(ligne)
    
    return jsonify({"message": f"{data['nom']} ajouté"}), 201

@app.route("/monstres/<nom>", methods=["DELETE"])
def supprimer_monstre(nom):
    if not verifier_token():
        return jsonify({"erreur": "Non autorisé"}), 401
    
    monstres = charger_monstres()
    
    nouveaux = []
    for m in monstres:
        if m["nom"].lower() != nom.lower():
            nouveaux.append(m)
    
    if len(nouveaux) == len(monstres):
        return jsonify({"erreur": "Monstre introuvable"}), 404
    
    with open("monsters.csv", "w") as f:
        for m in nouveaux:
            ligne = f"{m['categorie']};{m['nom']};{m['hp']};{m['atk']};{m['def']};{m['mercy']}\n"
            f.write(ligne)
    
    return jsonify({"message": f"{nom} supprimé"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)