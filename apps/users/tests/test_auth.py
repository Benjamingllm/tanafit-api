import pytest

from apps.users.models import User

EMAIL = "alice@example.com"
PASSWORD = "motdepasse-test-1"


@pytest.mark.django_db
def test_login_returns_tokens(client):
    User.objects.create_user(email=EMAIL, password=PASSWORD)

    response = client.post(
        "/api/auth/login/",
        data={"email": EMAIL, "password": PASSWORD},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert "access" in response.json()
    assert "refresh" in response.json()


@pytest.mark.django_db
def test_login_refuses_wrong_password(client):
    User.objects.create_user(email=EMAIL, password=PASSWORD)

    response = client.post(
        "/api/auth/login/",
        data={"email": EMAIL, "password": "mauvais-mot-de-passe"},
        content_type="application/json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_login_ignores_email_case(client):
    User.objects.create_user(email=EMAIL, password=PASSWORD)

    response = client.post(
        "/api/auth/login/",
        data={"email": EMAIL.upper(), "password": PASSWORD},
        content_type="application/json",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_refresh_returns_new_access_token(client):
    User.objects.create_user(email=EMAIL, password=PASSWORD)
    login = client.post(
        "/api/auth/login/",
        data={"email": EMAIL, "password": PASSWORD},
        content_type="application/json",
    )

    response = client.post(
        "/api/auth/refresh/",
        data={"refresh": login.json()["refresh"]},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert "access" in response.json()
