![Pipeline](https://github.com/Maxime-H-DA/rpg-pipeline/actions/workflows/pipeline.yml/badge.svg)

# Pipeline du RPG Alterdune

Ce repo contient le pipeline de sécurité que j'ai mis en place autour de mon projet RPG en C++.

L'idée était de prendre un vrai projet et lui appliquer des pratiques qu'on retrouve en entreprise — vérifier le code automatiquement, le compiler dans un environnement propre, et détecter des failles de sécurité à chaque modification.

## Ce qui se passe à chaque push

**Analyse du code avec Cppcheck**
Le code C++ est scanné automatiquement pour détecter des bugs et problèmes avant même la compilation. (même si le style de code est parfois remis en quesiton)

**Compilation dans Docker**
Le jeu est compilé dans un environnement isolé. N'importe qui peut le lancer sans avoir à installer quoi que ce soit sur sa machine.

**Scan de sécurité avec Trivy**
L'image Docker est analysée pour détecter des failles connues. Le premier scan a révélé une faille critique sur l'image de base, j'ai migré vers Alpine Linux et le scan suivant était propre.

## Outils utilisés

GitHub Actions, Docker, Cppcheck, Trivy

## Projet source

Le code du jeu RPG : [projet-RPG-S6](https://github.com/Maxime-H-DA/projet-RPG-S6)