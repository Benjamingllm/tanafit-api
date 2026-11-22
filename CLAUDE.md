# tanafit-api

Backend de Tanafit, une application de suivi de musculation. L'API servira un front Vue, puis une application mobile Expo.

## Stack

- Python 3.13, Django 5.2 LTS, Django REST Framework
- djangorestframework-simplejwt pour l'authentification par JWT
- PostgreSQL 17, pilote psycopg 3
- Docker Compose : services `web` (Django) et `db` (PostgreSQL)
- gunicorn et whitenoise pour l'image de production
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
docker compose exec -e DEBUG=False -e HTTPS=True web python manage.py check --deploy
docker build -t tanafit-api:prod .   # image de production
docker run --rm -p 8001:8000 --env-file .env -e DEBUG=False --network tanafit-api_default tanafit-api:prod
```

Dans PowerShell 5.1, `curl` est un alias d'`Invoke-WebRequest` : utiliser `curl.exe`. Une commande `sh -c '...'` avec des guillemets imbriqués passée à `docker` est mal transmise : la lancer depuis Bash.

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
- `Dockerfile` : cible `dev` (utilisée par docker compose) et cible `prod` (par défaut : code copié, statiques collectés, migrations puis gunicorn)
- `apps/core/` : routes techniques, dont `/api/health/`
- `apps/users/` : modèle `User` personnalisé, identifié par son e-mail (`AUTH_USER_MODEL = "users.User"`), et routes d'authentification sous `/api/auth/`
- `apps/<app>/tests/` : tests de chaque application, fichiers `test_*.py`
- `docs/` : notes techniques

## Conventions

### Code

- Une nouvelle application va dans `apps/`, avec `name = "apps.<nom>"` dans son `apps.py`, et s'ajoute à `INSTALLED_APPS`.
- Les routes de l'API sont sous le préfixe `/api/`.
- Toute route exige un jeton d'accès par défaut (`IsAuthenticated`). Une route publique le déclare explicitement avec `AllowAny`, comme `/api/health/`.
- Aucun secret dans le code : tout réglage sensible ou propre à un environnement est lu avec django-environ dans `config/settings.py`, et documenté dans `.env.example`.
- `DEBUG` vaut `False` et `HTTPS` vaut `True` par défaut. `SECRET_KEY` et `DATABASE_URL` n'ont pas de valeur de repli. `HTTPS=False` en développement et en CI, sinon chaque requête HTTP est redirigée.
- ruff : lignes de 100 caractères, règles `E`, `F`, `I`, `UP`, `B`, `DJ`. Les migrations sont exclues.
- Le mot de passe de la base ne contient que des lettres et des chiffres, sinon `DATABASE_URL` est mal découpée.

### Git

- `main` est stable : jamais de commit direct. Branches `feat/`, `fix/`, `chore/`, `docs/`, fusionnées par pull request en squash.
- Messages de commit courts, en français, à l'impératif, préfixés `feat:`, `fix:`, `chore:` ou `docs:`.
- Pas de ligne `Co-Authored-By` dans les commits.
- Ne jamais pousser sur GitHub : c'est le développeur qui le fait.

Le détail est dans `docs/git-et-github.md`.

## État du projet

Mise en place terminée, aucune fonctionnalité métier.

En place :

- squelette Django avec la route `GET /api/health/`, qui répond `{"status": "ok"}`
- modèle `User` identifié par son adresse e-mail, sans `username`, avec son manager (`User.objects.create_user(email=..., password=...)`) et son écran d'admin
- environnement Docker de développement, avec rechargement automatique du code
- connexion par JWT : `POST /api/auth/login/` (e-mail et mot de passe, insensible à la casse de l'e-mail) renvoie un jeton d'accès de 15 minutes et un jeton de rafraîchissement de 30 jours ; `POST /api/auth/refresh/` renouvelle les deux
- inscription : `POST /api/auth/register/` (publique) crée un compte à partir d'un e-mail et d'un mot de passe, refuse un e-mail déjà pris quelle que soit la casse et un mot de passe rejeté par `AUTH_PASSWORD_VALIDATORS`, et renvoie le compte créé, sans jetons
- profil : `GET /api/auth/me/` renvoie le compte connecté (`id`, `email`, `first_name`, `last_name`)
- sérialiseurs dans `apps/users/serializers.py` : `UserSerializer` pour exposer un compte, `RegisterSerializer` pour l'inscription
- ruff, pre-commit, pytest, avec des tests sur la route de santé, le CORS, le modèle `User`, la connexion, l'inscription et le profil
- workflow de CI
- CORS pour le front Vue
- image de production : gunicorn, fichiers statiques servis par whitenoise, logs sur la console
- réglages HTTPS activés par la variable `HTTPS` : redirection, HSTS d'une heure, cookies sécurisés, confiance dans l'en-tête `X-Forwarded-Proto` du proxy ; `/api/health/` reste accessible en HTTP

Pas encore fait :

- hébergement : plateforme ou VPS, certificat HTTPS, variables de production
- HSTS à passer à 1 an une fois HTTPS validé en production
- modèles et routes métier

## Historique

Les pull requests fusionnées sur `main`, dans l'ordre.

### Préparation du poste

- Outils installés et vérifiés : Git, Python, uv, Docker Desktop (Windows a dû redémarrer pour que `docker` soit reconnu).
- Smart App Control bloque sous Windows le pilote PostgreSQL et le lanceur de pre-commit. Décision : tout ce qui charge Django tourne dans Docker ; ruff et pre-commit passent par `uv run`.

### PR #1 : mise en place du projet

- Squelette Django 5.2 : `config/` pour les réglages, `apps/core` pour les routes techniques, `apps/users` pour les comptes.
- Réglages lus depuis `.env` avec django-environ, `.env.example` documenté, `.env` ignoré par Git.
- Modèle `User` personnalisé dès le départ, pour pouvoir le modifier plus tard sans migration douloureuse.
- Route `GET /api/health/`.
- Docker : Dockerfile Python 3.13 avec uv ; `docker-compose.yml` avec `web` et `db` (PostgreSQL 17), attente de la base, migrations au démarrage, rechargement du code.
- Qualité : ruff, pre-commit, pytest et pytest-django.
- CI GitHub Actions : jobs `Lint` et `Tests`, avec une base PostgreSQL.
- Git : `.gitignore`, `.gitattributes` (fins de ligne LF), GitHub Flow, convention de commits.
- Documentation : `README.md`, `CLAUDE.md`, `docs/git-et-github.md`.
- GitHub : `main` protégée par la règle `protection-main` (pull request obligatoire, `Lint` et `Tests` au vert, ni suppression ni force push).
- Problèmes rencontrés : un mot de passe de base avec des caractères spéciaux qui cassait `DATABASE_URL`, un bloc dupliqué dans le Dockerfile, un push parti par erreur sur `main` puis rattrapé par une pull request.

### PR #2 : CORS pour le front

- django-cors-headers, origines autorisées lues depuis `CORS_ALLOWED_ORIGINS` (`http://localhost:5173` pour Vue).
- Tests : une origine déclarée est acceptée, une origine inconnue est refusée.

### PR #3 : comptes identifiés par e-mail

- `UserManager` : `create_user` (e-mail obligatoire, nettoyé et passé en minuscules, mot de passe haché) et `create_superuser`.
- `User` sans `username`, e-mail unique comme identifiant ; écran d'admin adapté ; migration `0002`.
- Tests sur le modèle.

### PR #4 : connexion par JWT

- djangorestframework-simplejwt : jeton d'accès de 15 minutes, jeton de rafraîchissement de 30 jours, renouvelé à chaque usage.
- `IsAuthenticated` par défaut sur toutes les routes.
- Routes `POST /api/auth/login/` et `POST /api/auth/refresh/`.
- Connexion insensible à la casse de l'e-mail, via `UserManager.get_by_natural_key`.
- Tests sur la connexion et le rafraîchissement.

### PR #5 : inscription et profil

- `UserSerializer` pour exposer un compte ; `RegisterSerializer` qui vérifie l'unicité de l'e-mail sans tenir compte de la casse, applique les règles de mot de passe de Django et crée le compte avec `create_user`.
- Route publique `POST /api/auth/register/`, qui renvoie le compte créé (201).
- Route `GET /api/auth/me/`, qui renvoie le compte connecté.
- Tests sur l'inscription et le profil. La suite compte 16 tests.

### PR #6 : image et réglages de production

- gunicorn remplace `runserver` dans l'image de production ; whitenoise sert les statiques compressés, avec une empreinte dans leur nom.
- Dockerfile en deux cibles : `dev` pour docker compose, `prod` par défaut. `collectstatic` tourne à la construction avec des valeurs factices de `SECRET_KEY` et `DATABASE_URL`.
- Variable `HTTPS`, vraie par défaut : redirection, HSTS, cookies sécurisés, `SECURE_PROXY_SSL_HEADER`. Mise à `False` dans `.env` et dans la CI.
- Logs sur la console : avec `DEBUG=False`, Django n'affichait pas les erreurs 500.
- Avertissement de whitenoise sur l'absence de `staticfiles/` masqué dans pytest.
- Vérifié : `check --deploy` (seul reste `security.W021`, preload volontairement désactivé), image de production lancée en local, redirection, HSTS et cookie `Secure` contrôlés avec curl.
- Problèmes rencontrés : middlewares ajoutés en double en fin de liste, et `USER app` dans l'étape de base qui empêchait les étapes suivantes d'écrire dans l'image.
