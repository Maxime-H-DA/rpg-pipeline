![Pipeline](https://github.com/Maxime-H-DA/rpg-pipeline/actions/workflows/pipeline.yml/badge.svg)

# Pipeline du RPG Alterdune

Ce repo contient le pipeline de sécurité que j'ai mis en place autour de mon projet RPG en C++.

L'idée était de prendre un vrai projet et lui appliquer des pratiques qu'on retrouve en entreprise — vérifier le code automatiquement, le compiler dans un environnement propre, et détecter des failles de sécurité à chaque modification.

## Ce qui se passe à chaque push

**Analyse du code avec Cppcheck**
Le code C++ est scanné automatiquement pour détecter des bugs et problèmes avant même la compilation.

**Compilation dans Docker**
Le jeu est compilé dans un environnement isolé. N'importe qui peut le lancer sans avoir à installer quoi que ce soit sur sa machine.

**Scan de sécurité avec Trivy**
L'image Docker est analysée pour détecter des failles connues. Le premier scan a révélé une faille critique sur l'image de base, j'ai migré vers Alpine Linux et le scan suivant était propre.

## L'API du bestiaire

Une API Flask déployée sur [rpg-pipeline.onrender.com](https://rpg-pipeline.onrender.com) qui expose les données des monstres du jeu. La lecture est libre, les modifications nécessitent une connexion avec identifiant et mot de passe.

## Synchronisation avec le jeu

Pour jouer avec les données en ligne plutôt que les données locales :

```bash
py play.py
```

Le script récupère les monstres depuis l'API et met à jour le fichier `monsters.csv` utilisé par le jeu.

## Outils utilisés

GitHub Actions, Docker, Cppcheck, Gitleaks, Trivy, Flask, SQLite, JWT

## Administration

- Dashboard Render : [Gérer le serveur](https://dashboard.render.com/web/srv-d8a0udp9rddc739m5itg)

## Projet source

Le code du jeu RPG : [projet-RPG-S6](https://github.com/Maxime-H-DA/projet-RPG-S6)