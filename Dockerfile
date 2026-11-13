
FROM python:3.13-slim

# uv, le gestionnaire de dépendances, copié depuis son image officielle
COPY --from=ghcr.io/astral-sh/uv:0.12.24 /uv /bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=0 \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Les dépendances d'abord : cette couche reste en cache tant que uv.lock ne change pas
COPY pyproject.toml uv.lock ./
RUN uv sync --locked

COPY . .

# Ne pas tourner en root dans le conteneur
RUN useradd --create-home app
USER app

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]