# tanafit-api

Backend de **Tanafit**, une application de suivi de musculation. Cette API servira d'abord un front Vue, puis une application mobile Expo.

Le projet en est à sa mise en place : il ne contient encore aucune fonctionnalité métier, seulement un socle Django prêt à en recevoir.

## Stack

| Rôle | Outil |
|---|---|
| Langage | Python 3.13 |
| Framework | Django 5.2 LTS, Django REST Framework |
| Base de données | PostgreSQL 17 |
| Environnement | Docker et Docker Compose |
| Dépendances | uv (`pyproject.toml` et `uv.lock`) |
| Qualité | ruff (lint et formatage), pre-commit |
| Tests | pytest, pytest-django |
| Intégration continue | GitHub Actions |

## Prérequis

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/), avec le moteur WSL 2 sous Windows
- [uv](https://docs.astral.sh/uv/), pour gérer les dépendances et lancer ruff et pre-commit

Python n'a pas besoin d'être installé à part : l'application tourne dans Docker, et uv télécharge lui-même la bonne version pour les outils locaux.

## Installation

**1. Récupérer le projet**

```powershell
git clone <url-du-depot>
cd tanafit-api
```

**2. Créer le fichier de configuration**

```powershell
copy .env.example .env
```

Ouvrir `.env` et remplacer les deux valeurs factices :

- `SECRET_KEY` : générer une clé avec
  `uv run python -c "import secrets; print(secrets.token_urlsafe(50))"`
- le mot de passe de la base, à l'identique dans `POSTGRES_PASSWORD` et dans `DATABASE_URL`. Utiliser uniquement des lettres et des chiffres : les caractères spéciaux cassent l'URL de connexion.

Le fichier `.env` contient des secrets et n'est jamais commité.

**3. Lancer l'application**

```powershell
docker compose up -d --build
```

Docker construit l'image, démarre PostgreSQL, attend que la base soit prête, applique les migrations puis lance le serveur.

**4. Vérifier**

Ouvrir <http://localhost:8000/api/health/> : la réponse doit être `{"status": "ok"}`.

**5. Installer les outils de développement**

```powershell
uv sync
uv run python -m pre_commit install
```

À partir de là, ruff vérifie et met en forme le code à chaque `git commit`.

## Commandes utiles

### Au quotidien

| Action | Commande |
|---|---|
| Lancer | `docker compose up -d` |
| Arrêter | `docker compose down` |
| Voir les logs | `docker compose logs -f web` |
| Lancer les tests | `docker compose exec web pytest` |
| Ouvrir un shell Django | `docker compose exec web python manage.py shell` |
| Créer un superuser | `docker compose exec web python manage.py createsuperuser` |

L'admin Django est ensuite disponible sur <http://localhost:8000/admin/>.

Le code est monté dans le conteneur : le serveur redémarre tout seul quand un fichier change.

### Base de données et migrations

| Action | Commande |
|---|---|
| Créer une migration après un changement de modèle | `docker compose exec web python manage.py makemigrations` |
| Appliquer les migrations | `docker compose exec web python manage.py migrate` |
| Repartir d'une base vide | `docker compose down -v` |

Les migrations sont aussi appliquées automatiquement à chaque démarrage.

`docker compose down -v` supprime le volume PostgreSQL : **toutes les données de la base sont effacées**.

### Dépendances

| Action | Commande |
|---|---|
| Ajouter une dépendance | `uv add <paquet>` |
| Ajouter un outil de développement | `uv add --dev <paquet>` |
| Reconstruire l'image après un ajout | `docker compose up -d --build` |

### Qualité du code

| Action | Commande |
|---|---|
| Vérifier le code | `uv run ruff check .` |
| Mettre en forme | `uv run ruff format .` |
| Lancer tous les hooks | `uv run python -m pre_commit run --all-files` |

### Ménage

`docker system prune` supprime les images et le cache de build inutilisés, qui s'accumulent avec le temps.

## Particularité sous Windows : Smart App Control

Si Smart App Control est activé, Windows bloque certains fichiers non signés, dont le pilote PostgreSQL de Python. Deux conséquences :

- les commandes Django (`manage.py`, `pytest`) se lancent **dans le conteneur**, avec `docker compose exec web ...`, et non directement sous Windows ;
- pre-commit s'appelle avec `uv run python -m pre_commit ...`, la forme courte `pre-commit` étant bloquée.

Les commandes de ce README tiennent déjà compte de ces deux points.

## Organisation du projet

```
tanafit-api/
├── .github/workflows/   # intégration continue
├── apps/                # les applications Django
│   ├── core/            # routes techniques (/api/health/)
│   └── users/           # modèle User personnalisé
├── config/              # réglages, routes principales, points d'entrée
├── docs/                # notes techniques
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── pyproject.toml       # dépendances, configuration de ruff et de pytest
```

Les tests de chaque application sont dans son dossier `tests/`.

Tous les réglages sensibles sont lus dans les variables d'environnement. `DEBUG` vaut `False` si la variable est absente, et l'application refuse de démarrer sans `SECRET_KEY` ni `DATABASE_URL`.

## Branches et commits

`main` est toujours stable. On n'y commite jamais directement : chaque changement passe par une branche courte et une pull request.

| Préfixe de branche | Usage | Exemple |
|---|---|---|
| `feat/` | nouvelle fonctionnalité | `feat/creation-seance` |
| `fix/` | correction de bug | `fix/calcul-volume` |
| `chore/` | outillage, configuration, maintenance | `chore/mise-a-jour-django` |
| `docs/` | documentation | `docs/guide-installation` |

Les messages de commit sont courts, en français, à l'impératif présent, et commencent par le même préfixe :

```
feat: ajoute la création d'une séance
fix: corrige le calcul du volume total
chore: met à jour Django
docs: complète le guide d'installation
```

Le cycle de travail complet et les réglages du dépôt GitHub sont décrits dans [docs/git-et-github.md](docs/git-et-github.md).
