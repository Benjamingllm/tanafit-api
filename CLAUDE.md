# tanafit-api

Backend de Tanafit, une application de suivi de musculation. L'API servira un front Vue, puis une application mobile Expo.

## Stack

- Python 3.13, Django 5.2 LTS, Django REST Framework
- PostgreSQL 17, pilote psycopg 3
- Docker Compose : services `web` (Django) et `db` (PostgreSQL)
- uv pour les dépendances (`pyproject.toml`, `uv.lock`)
- ruff (lint et formatage), pre-commit
- pytest et pytest-django
- GitHub Actions : jobs `Lint` et `Tests` sur chaque pull request

## Commandes

Le poste de développement est sous Windows avec Smart App Control activé : le pilote PostgreSQL est bloqué hors de Docker. Toute commande qui charge Django passe donc par le conteneur.

```powershell
docker compose up -d                 # lancer
docker compose up -d --build         # lancer après un changement de dépendances
docker compose down                  # arrêter
docker compose logs -f web           # logs
docker compose exec web pytest       # tests
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py shell
docker compose exec web python manage.py createsuperuser
```

Les outils sans base de données tournent sous Windows :

```powershell
uv add <paquet>                               # dépendance
uv add --dev <paquet>                         # outil de développement
uv run ruff check .
uv run ruff format .
uv run python -m pre_commit run --all-files   # pas `pre-commit` : le lanceur .exe est bloqué
```

`docker compose down -v` efface la base : ne pas l'utiliser sans demande explicite.

## Structure

- `config/` : `settings.py`, `urls.py`, points d'entrée WSGI et ASGI
- `apps/core/` : routes techniques, dont `/api/health/`
- `apps/users/` : modèle `User` personnalisé (`AUTH_USER_MODEL = "users.User"`)
- `apps/<app>/tests/` : tests de chaque application, fichiers `test_*.py`
- `docs/` : notes techniques

## Conventions

### Code

- Une nouvelle application va dans `apps/`, avec `name = "apps.<nom>"` dans son `apps.py`, et s'ajoute à `INSTALLED_APPS`.
- Les routes de l'API sont sous le préfixe `/api/`.
- Aucun secret dans le code : tout réglage sensible ou propre à un environnement est lu avec django-environ dans `config/settings.py`, et documenté dans `.env.example`.
- `DEBUG` vaut `False` par défaut. `SECRET_KEY` et `DATABASE_URL` n'ont pas de valeur de repli.
- ruff : lignes de 100 caractères, règles `E`, `F`, `I`, `UP`, `B`, `DJ`. Les migrations sont exclues.
- Le mot de passe de la base ne contient que des lettres et des chiffres, sinon `DATABASE_URL` est mal découpée.

### Git

- `main` est stable : jamais de commit direct. Branches `feat/`, `fix/`, `chore/`, `docs/`, fusionnées par pull request en squash.
- Messages de commit courts, en français, à l'impératif, préfixés `feat:`, `fix:`, `chore:` ou `docs:`.
- Pas de ligne `Co-Authored-By` dans les commits.
- Ne jamais pousser sur GitHub : c'est le développeur qui le fait.

Le détail est dans `docs/git-et-github.md`.

### Façon de travailler

Le développeur réalise les changements lui-même pour apprendre. Donner les étapes, les commandes et les explications, et n'écrire ou modifier des fichiers que sur demande explicite.

## État du projet

Mise en place terminée, aucune fonctionnalité métier.

En place :

- squelette Django avec la route `GET /api/health/`, qui répond `{"status": "ok"}`
- modèle `User` vide, hérité de `AbstractUser`, et sa migration initiale
- environnement Docker de développement, avec rechargement automatique du code
- ruff, pre-commit, pytest, un test sur la route de santé
- workflow de CI
- CORS pour le front Vue


Pas encore fait :

- authentification de l'API (jetons ou JWT pour le front et le mobile)
- réglages et image de production (serveur WSGI, fichiers statiques, HTTPS)
- modèles et routes métier
