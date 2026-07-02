![Pipeline](https://github.com/Maxime-H-DA/rpg-pipeline/actions/workflows/pipeline.yml/badge.svg)

### ENGLISH BELOW

# Pipeline du RPG Alterdune

Pipeline CI/CD sécurisé autour de mon projet RPG en C++ — vérification automatique du code, compilation dans un environnement isolé, et détection de failles de sécurité à chaque modification (SAST, DAST, scan de conteneurs, sécurité supply chain, déploiement Kubernetes).

L'idée était de prendre un vrai projet et lui appliquer des pratiques qu'on retrouve en entreprise.

## Avant même le push

Des hooks pre-commit tournent en local à chaque commit — Gitleaks, Bandit et Checkov refont les mêmes vérifications qu'en CI mais avant que le code parte sur GitHub, en plus de quelques hooks d'hygiène (espaces en fin de ligne, fichiers volumineux, YAML valide).

## Ce qui se passe à chaque push

```
push (main)
 ├─► analyse-code : Cppcheck (code C++)
 ├─► scan-jeu : Build Docker (jeu) + Trivy
 ├─► scan-api : Build Docker (API) + Trivy
 ├─► sast-api : Bandit + Semgrep
 ├─► tests-api : pytest
 ├─► dast-api : OWASP ZAP sur l'API déjà en ligne (Render)
 ├─► supply-chain-api : SBOM (Syft) + signature de l'image (Cosign)
 └─► iac-scan-checkov : scan des manifests Kubernetes et du chart Helm
```

Les 8 jobs tournent en parallèle à chaque push, sans dépendance entre eux. Render déploie automatiquement de son côté ; `dast-api` se contente de réveiller puis scanner l'API déjà en ligne.

**Analyse du code avec Cppcheck**
Le code C++ est scanné automatiquement pour détecter des bugs et problèmes avant même la compilation.

**Compilation dans Docker**
Le jeu est compilé dans un environnement isolé, avec un encodage forcé en UTF-8 pour que ça tourne pareil sous Windows, Mac ou Linux. N'importe qui peut le lancer sans avoir à installer quoi que ce soit sur sa machine.

**Scan de sécurité avec Trivy**
L'image Docker est analysée pour détecter des failles connues. Le premier scan a révélé une faille critique sur l'image de base utilisée pour compiler le jeu — migration vers Alpine Linux, le scan suivant était propre.

**Analyse statique Python (Bandit + Semgrep)**
L'API Flask est analysée avec deux outils complémentaires — Bandit détecte les vulnérabilités Python classiques, Semgrep applique les règles OWASP sur la sémantique du code.

**Test d'intrusion automatisé (OWASP ZAP)**
À chaque push, ZAP teste l'API directement en production comme le ferait un attaquant externe. Le premier scan a remonté 7 problèmes de configuration HTTP — headers de sécurité manquants (nosniff, CSP, HSTS), pas de politique de cache sur les routes sensibles. Tous corrigés dans `app.py`.

**Sécurité supply chain (Syft + Cosign)**
Chaque image poussée sur GitHub Container Registry génère un inventaire de ses dépendances (SBOM, format SPDX) et est signée en mode keyless via Sigstore — aucune clé privée à gérer, la signature s'appuie sur l'identité du workflow GitHub Actions et est publiée dans un registre de transparence public (Rekor).

**Scan d'infrastructure avec Checkov**
Les manifests Kubernetes et le chart Helm sont analysés à chaque push. Le premier scan a remonté 9 mauvaises configurations : UID trop bas (risque de collision avec un utilisateur hôte), secrets injectés en variables d'environnement au lieu de fichiers montés, système de fichiers du conteneur accessible en écriture, absence de politique réseau. 7 ont été corrigées dans les manifests et reproduites à l'identique dans le chart Helm ; les 2 restantes sont documentées et acceptées comme contraintes propres à Kind (pas de digest d'image disponible pour une image chargée localement, `imagePullPolicy` forcé à `IfNotPresent`).

**Tests unitaires (pytest)**
L'API est couverte par 36 tests unitaires — authentification JWT, validation des données, gestion des erreurs, headers de sécurité, lecture des secrets depuis fichiers montés ou variables d'environnement. Les tests tournent sur une base SQLite isolée pour ne pas polluer les données de production.

## L'API du bestiaire

Une API Flask déployée sur [rpg-pipeline.onrender.com](https://rpg-pipeline.onrender.com) qui expose les données des monstres du jeu. La lecture est libre, les modifications nécessitent une connexion avec identifiant et mot de passe.

### Docker

Pour tester l'API en local sans impacter la version en ligne — utile pour tester des modifications de code avant de les déployer :

```bash
docker build -t rpg-api -f rpg-api/Dockerfile .
docker run -d -p 5000:5000 --env-file .env -v rpg-data:/app/data rpg-api
```

L'API est alors accessible sur **http://localhost:5000**

### Kubernetes

L'API tourne aussi sur un cluster Kubernetes local avec Kind. Le conteneur s'exécute en non-root avec un système de fichiers en lecture seule, des ressources CPU et mémoire limitées, et des probes de santé qui surveillent que l'API répond. Les secrets sont injectés sous forme de fichiers montés plutôt qu'en variables d'environnement. Les 2 réplicas partagent un volume persistant (PVC) pour la base SQLite — sans ça, chaque pod aurait sa propre base isolée et les données auraient été incohérentes selon le pod qui répondait.

```bash
kind create cluster --config k8s/kind-config.yaml
docker build -t rpg-api:local -f rpg-api/Dockerfile .
kind load docker-image rpg-api:local --name rpg-pipeline
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/05-pvc.yaml
kubectl create secret generic rpg-api-secret --namespace rpg-pipeline --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f k8s/02-deployment.yaml
kubectl apply -f k8s/03-service.yaml
kubectl rollout restart deployment/rpg-api -n rpg-pipeline
kubectl port-forward -n rpg-pipeline svc/rpg-api 5000:80
```

L'API est alors accessible sur **http://localhost:5000**

Note : avec les deux méthodes, les modifications faites en local ne sont pas synchronisées avec la version en ligne.

### Helm

Le même déploiement existe aussi packagé en chart Helm (`helm/rpg-api/`). Toutes les valeurs configurables (réplicas, ressources, UID, taille du volume...) sont centralisées dans `values.yaml` — changer l'environnement ne nécessite de modifier qu'un seul fichier, pas les manifests un par un. Le chart est scanné par Checkov en CI et produit le même résultat que les manifests bruts.

```bash
kind create cluster --config k8s/kind-config.yaml
docker build -t rpg-api:local -f rpg-api/Dockerfile .
kind load docker-image rpg-api:local --name rpg-pipeline
helm install rpg-api helm/rpg-api --namespace rpg-pipeline --create-namespace
kubectl create secret generic rpg-api-secret --namespace rpg-pipeline --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout restart deployment/rpg-api -n rpg-pipeline
kubectl port-forward -n rpg-pipeline svc/rpg-api 5000:80
```

L'API est alors accessible sur **http://localhost:5000**

## Synchronisation avec le jeu

Pour jouer avec les données en ligne plutôt que les données locales :

```bash
py play.py
```

`monsters.csv` est la copie locale des monstres du jeu C++, régénérée à chaque lancement. Le script récupère les monstres depuis l'API et met à jour ce fichier avant que le jeu démarre.

## Outils utilisés

- **CI/CD & infrastructure** : GitHub Actions, Docker, Kubernetes (Kind), Helm, Alpine Linux
- **Sécurité** : Gitleaks, Trivy, Bandit, Semgrep, OWASP ZAP, Cppcheck, Checkov, Syft, Cosign
- **Backend & tests** : Flask, SQLite, JWT, pytest

## Projet source

Le code du jeu RPG : [projet-RPG-S6](https://github.com/Maxime-H-DA/projet-RPG-S6)

------------------------------------------------------------------------------------------

![Pipeline](https://github.com/Maxime-H-DA/rpg-pipeline/actions/workflows/pipeline.yml/badge.svg)

# Alterdune RPG Pipeline

Secure CI/CD pipeline around my C++ RPG project — automatic code checks, compilation in an isolated environment, and security vulnerability detection on every change (SAST, DAST, container scanning, supply chain security, Kubernetes deployment).

The idea was to take a real project and apply practices found in professional environments.

## Before the push even happens

Pre-commit hooks run locally on every commit — Gitleaks, Bandit, and Checkov run the same checks as CI before the code reaches GitHub, plus a few hygiene hooks (trailing whitespace, large files, valid YAML).

## What happens on every push

```
push (main)
 ├─► analyse-code : Cppcheck (C++ code)
 ├─► scan-jeu : Docker build (game) + Trivy
 ├─► scan-api : Docker build (API) + Trivy
 ├─► sast-api : Bandit + Semgrep
 ├─► tests-api : pytest
 ├─► dast-api : OWASP ZAP against the live API (Render)
 ├─► supply-chain-api : SBOM (Syft) + image signing (Cosign)
 └─► iac-scan-checkov : Kubernetes manifest and Helm chart scanning
```

All 8 jobs run in parallel on every push, with no dependencies between them. Render deploys automatically on its own; `dast-api` just wakes up and scans the API that's already live.

**Code analysis with Cppcheck**
The C++ code is automatically scanned to detect bugs and issues before compilation even starts.

**Compilation in Docker**
The game is compiled in an isolated environment, with UTF-8 encoding forced so it behaves the same on Windows, Mac, or Linux. Anyone can run it without having to install anything on their machine.

**Security scan with Trivy**
The Docker image is analyzed to detect known vulnerabilities. The first scan revealed a critical flaw in the base image used to build the game — migrated to Alpine Linux, the next scan came back clean.

**Python static analysis (Bandit + Semgrep)**
The Flask API is analyzed with two complementary tools — Bandit detects classic Python vulnerabilities, Semgrep applies OWASP rules to the code's semantics.

**Automated penetration testing (OWASP ZAP)**
On every push, ZAP tests the API directly in production the way an external attacker would. The first scan flagged 7 HTTP configuration issues — missing security headers (nosniff, CSP, HSTS), no caching policy on sensitive routes. All fixed in `app.py`.

**Supply chain security (Syft + Cosign)**
Every image pushed to GitHub Container Registry gets a dependency inventory (SBOM, SPDX format) and is signed keyless via Sigstore — no private key to manage, the signature relies on the GitHub Actions workflow identity and is published to a public transparency log (Rekor).

**Infrastructure scanning with Checkov**
Kubernetes manifests and the Helm chart are scanned on every push. The first scan flagged 9 misconfigurations: UID too low (risk of collision with a host user), secrets injected as environment variables instead of mounted files, writable container filesystem, missing network policy. 7 were fixed in the manifests and reproduced identically in the Helm chart; the remaining 2 are documented and accepted as constraints specific to Kind (no image digest available for a locally loaded image, `imagePullPolicy` forced to `IfNotPresent`).

**Unit tests (pytest)**
The API is covered by 36 unit tests — JWT authentication, data validation, error handling, security headers, secret reading from mounted files or environment variables. Tests run on an isolated SQLite database to avoid polluting production data.

## The Bestiary API

A Flask API deployed at [rpg-pipeline.onrender.com](https://rpg-pipeline.onrender.com) that exposes the game's monster data. Reading is open, modifications require authentication with a username and password.

### Docker

To test the API locally without impacting the live version — useful for testing code changes before deploying:

```bash
docker build -t rpg-api -f rpg-api/Dockerfile .
docker run -d -p 5000:5000 --env-file .env -v rpg-data:/app/data rpg-api
```

The API is then available at **http://localhost:5000**

### Kubernetes

The API also runs on a local Kubernetes cluster with Kind. The container runs as non-root with a read-only filesystem, capped CPU and memory, and health probes that monitor whether the API responds. Secrets are injected as mounted files rather than environment variables. The 2 replicas share a persistent volume (PVC) for the SQLite database — without it, each pod would have its own isolated database and data would have been inconsistent depending on which pod responded.

```bash
kind create cluster --config k8s/kind-config.yaml
docker build -t rpg-api:local -f rpg-api/Dockerfile .
kind load docker-image rpg-api:local --name rpg-pipeline
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/05-pvc.yaml
kubectl create secret generic rpg-api-secret --namespace rpg-pipeline --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f k8s/02-deployment.yaml
kubectl apply -f k8s/03-service.yaml
kubectl rollout restart deployment/rpg-api -n rpg-pipeline
kubectl port-forward -n rpg-pipeline svc/rpg-api 5000:80
```

The API is then available at **http://localhost:5000**

Note: with either method, local changes are not synced with the live version.

### Helm

The same deployment is also packaged as a Helm chart (`helm/rpg-api/`). All configurable values (replicas, resources, UID, volume size...) are centralized in `values.yaml` — switching environments only requires changing one file, not editing manifests one by one. The chart is scanned by Checkov in CI and produces the same result as the raw manifests.

```bash
kind create cluster --config k8s/kind-config.yaml
docker build -t rpg-api:local -f rpg-api/Dockerfile .
kind load docker-image rpg-api:local --name rpg-pipeline
helm install rpg-api helm/rpg-api --namespace rpg-pipeline --create-namespace
kubectl create secret generic rpg-api-secret --namespace rpg-pipeline --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout restart deployment/rpg-api -n rpg-pipeline
kubectl port-forward -n rpg-pipeline svc/rpg-api 5000:80
```

The API is then available at **http://localhost:5000**

## Syncing with the game

To play with the live data instead of local data:

```bash
py play.py
```

`monsters.csv` is the local copy of the C++ game's monsters, regenerated on every launch. The script fetches monsters from the API and updates this file before the game starts.

## Tools used

- **CI/CD & infrastructure**: GitHub Actions, Docker, Kubernetes (Kind), Helm, Alpine Linux
- **Security**: Gitleaks, Trivy, Bandit, Semgrep, OWASP ZAP, Cppcheck, Checkov, Syft, Cosign
- **Backend & testing**: Flask, SQLite, JWT, pytest

## Source project

The RPG game code: [projet-RPG-S6](https://github.com/Maxime-H-DA/projet-RPG-S6)
