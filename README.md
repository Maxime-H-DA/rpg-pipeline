![Pipeline](https://github.com/Maxime-H-DA/rpg-pipeline/actions/workflows/pipeline.yml/badge.svg)


### ENGLISH BELOW


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

**Analyse statique Python (Bandit + Semgrep)**
L'API Flask est analysée avec deux outils complémentaires — Bandit détecte les vulnérabilités Python classiques, Semgrep applique les règles OWASP sur la sémantique du code.

**Test d'intrusion automatisé (OWASP ZAP)**
À chaque push, ZAP teste l'API directement en production comme le ferait un attaquant externe. Les premiers rapports ont révélé 7 problèmes de configuration HTTP — headers de sécurité manquants, politique CSP absente, styles inline. Tous ont été corrigés itérativement.

**Tests unitaires (pytest)**
L'API est couverte par 31 tests unitaires — authentification JWT, validation des données, gestion des erreurs, headers de sécurité. Les tests tournent sur une base SQLite isolée pour ne pas polluer les données de production.

## L'API du bestiaire

Une API Flask déployée sur [rpg-pipeline.onrender.com](https://rpg-pipeline.onrender.com) qui expose les données des monstres du jeu. La lecture est libre, les modifications nécessitent une connexion avec identifiant et mot de passe.

Pour tester l'API en local sans impacter la version en ligne — utile pour tester des modifications de code avant de les déployer :

```bash
docker build -t rpg-api -f rpg-api/Dockerfile .
docker run -d -p 5000:5000 --env-file .env -v rpg-data:/app/data rpg-api
```

Note : les modifications faites en local ne sont pas synchronisées avec la version en ligne.

## Synchronisation avec le jeu

Pour jouer avec les données en ligne plutôt que les données locales :

```bash
py play.py
```

Le script récupère les monstres depuis l'API et met à jour le fichier `monsters.csv` utilisé par le jeu.

## Outils utilisés

GitHub Actions, Docker, Alpine Linux, Cppcheck, Gitleaks, Trivy, Bandit, Semgrep, OWASP ZAP, pytest, Flask, SQLite, JWT

## Administration

- Dashboard Render : [Gérer le serveur](https://dashboard.render.com/web/srv-d8ab07jeo5us739hn4d0)

## Projet source

Le code du jeu RPG : [projet-RPG-S6](https://github.com/Maxime-H-DA/projet-RPG-S6)


------------------------------------------------------------------------------------------


![Pipeline](https://github.com/Maxime-H-DA/rpg-pipeline/actions/workflows/pipeline.yml/badge.svg)

# Alterdune RPG Pipeline

This repository contains the security pipeline I built around my C++ RPG project.

The idea was to take a real project and apply practices found in professional environments — automatically checking the code, compiling it in a clean environment, and detecting security vulnerabilities on every change.

## What happens on every push

**Code analysis with Cppcheck**
The C++ code is automatically scanned to detect bugs and issues before compilation even starts.

**Compilation in Docker**
The game is compiled in an isolated environment. Anyone can run it without having to install anything on their machine.

**Security scan with Trivy**
The Docker image is analyzed to detect known vulnerabilities. The first scan revealed a critical flaw in the base image — I migrated to Alpine Linux and the next scan came back clean.

**Python static analysis (Bandit + Semgrep)**
The Flask API is analyzed with two complementary tools — Bandit detects classic Python vulnerabilities, Semgrep applies OWASP rules to the code's semantics.

**Automated penetration testing (OWASP ZAP)**
On every push, ZAP tests the API directly in production the way an external attacker would. The first reports revealed 7 HTTP configuration issues — missing security headers, absent CSP policy, inline styles. All were fixed iteratively.

**Unit tests (pytest)**
The API is covered by 31 unit tests — JWT authentication, data validation, error handling, security headers. Tests run on an isolated SQLite database to avoid polluting production data.

## The Bestiary API

A Flask API deployed at [rpg-pipeline.onrender.com](https://rpg-pipeline.onrender.com) that exposes the game's monster data. Reading is open, modifications require authentication with a username and password.

To test the API locally without impacting the live version — useful for testing code changes before deploying:

```bash
docker build -t rpg-api -f rpg-api/Dockerfile .
docker run -d -p 5000:5000 --env-file .env -v rpg-data:/app/data rpg-api
```

Note: local changes are not synced with the live version.

## Syncing with the game

To play with the live data instead of local data:

```bash
py play.py
```

The script fetches monsters from the API and updates the `monsters.csv` file used by the game.

## Tools used

GitHub Actions, Docker, Alpine Linux, Cppcheck, Gitleaks, Trivy, Bandit, Semgrep, OWASP ZAP, pytest, Flask, SQLite, JWT

## Administration

- Render Dashboard: [Manage the server](https://dashboard.render.com/web/srv-d8ab07jeo5us739hn4d0)

## Source project

The RPG game code: [projet-RPG-S6](https://github.com/Maxime-H-DA/projet-RPG-S6)