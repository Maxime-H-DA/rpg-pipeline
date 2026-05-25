import urllib.request
import json
import os

API_URL = "https://rpg-pipeline.onrender.com/monstres"
CSV_PATH = os.path.join(os.path.dirname(__file__), "rpg-source", "monsters.csv")

print("Connexion a l'API en ligne...")

try:
    with urllib.request.urlopen(API_URL, timeout=10) as reponse:
        monstres = json.loads(reponse.read().decode())

    with open(CSV_PATH, "w", encoding="utf-8") as f:
        for m in monstres:
            f.write(f"{m['categorie']};{m['nom']};{m['hp']};{m['atk']};{m['def']};{m['mercy']}\n")

    print(f"{len(monstres)} monstres recuperes depuis l'API")
    print("Le fichier monsters.csv a ete mis a jour")
    print("On joue avec les donnees en ligne")

except Exception as e:
    print(f"Impossible de contacter l'API : {e}")
    print("On joue avec les donnees locales")