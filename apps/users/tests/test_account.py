import pytest

from apps.users.models import User

EMAIL = "alice@example.com"
PASSWORD = "motdepasse-test-1"


@pytest.mark.django_db
def test_register_creates_account(client):
    response = client.post(
        "/api/auth/register/",
        data={"email": "Alice@Example.com", "password": PASSWORD},
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.json()["email"] == EMAIL
    assert "password" not in response.json()


@pytest.mark.django_db
def test_register_refuses_existing_email(client):
    User.objects.create_user(email=EMAIL, password=PASSWORD)

    response = client.post(
        "/api/auth/register/",
        data={"email": EMAIL.upper(), "password": PASSWORD},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "email" in response.json()


@pytest.mark.django_db
def test_register_refuses_weak_password(client):
    response = client.post(
        "/api/auth/register/",
        data={"email": EMAIL, "password": "123"},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "password" in response.json()


@pytest.mark.django_db
def test_me_requires_token(client):
    response = client.get("/api/auth/me/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_me_returns_connected_user(client):
    User.objects.create_user(email=EMAIL, password=PASSWORD)
    login = client.post(
        "/api/auth/login/",
        data={"email": EMAIL, "password": PASSWORD},
        content_type="application/json",
    )
    token = login.json()["access"]

    response = client.get("/api/auth/me/", headers={"Authorization": "Bearer " + token})

    assert response.status_code == 200
    assert response.json()["email"] == EMAIL
