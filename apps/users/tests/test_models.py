import pytest
from django.db import IntegrityError

from apps.users.models import User


@pytest.mark.django_db
def test_create_user_cleans_email_and_hashes_password():
    user = User.objects.create_user(email="  Alice@Example.COM ", password="motdepasse-test-1")

    assert user.email == "alice@example.com"
    assert user.check_password("motdepasse-test-1")
    assert not user.is_staff


@pytest.mark.django_db
def test_create_superuser_has_all_rights():
    admin = User.objects.create_superuser(email="admin@example.com", password="motdepasse-test-1")

    assert admin.is_staff
    assert admin.is_superuser


@pytest.mark.django_db
def test_duplicate_email_is_refused():
    User.objects.create_user(email="alice@example.com", password="motdepasse-test-1")

    with pytest.raises(IntegrityError):
        User.objects.create_user(email="alice@example.com", password="motdepasse-test-1")


def test_email_is_required():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="motdepasse-test-1")
