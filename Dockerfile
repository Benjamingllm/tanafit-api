FROM python:3.13-slim AS base

# uv, le gestionnaire de dépendances, copié depuis son image officielle
COPY --from=ghcr.io/astral-sh/uv:0.12.24 /uv /bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=0 \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Dépendances de production seulement ; la couche reste en cache tant que uv.lock ne change pas
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

# Utilisateur sans droits d'administration, activé à la fin de chaque cible
RUN useradd --create-home app


# Développement : outils de dev en plus, le code est monté par docker compose
FROM base AS dev
RUN uv sync --locked
USER app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# Production : le code est copié dans l'image et servi par gunicorn (cible par défaut)
FROM base AS prod
COPY . .
# Les réglages exigent SECRET_KEY et DATABASE_URL. Des valeurs factices suffisent :
# collectstatic ne se connecte pas à la base.
RUN SECRET_KEY=build DATABASE_URL=postgres://build@localhost/build \
    python manage.py collectstatic --noinput
USER app
EXPOSE 8000
# exec : gunicorn devient le processus principal et reçoit le signal d'arrêt de Docker
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --access-logfile -"]
