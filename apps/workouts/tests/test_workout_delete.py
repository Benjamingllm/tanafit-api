from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User
from apps.workouts.models import Workout

PASSWORD = "motdepasse-test-1"


@pytest.fixture
def alice(db):
    return User.objects.create_user(email="alice@example.com", password=PASSWORD)


@pytest.fixture
def bob(db):
    return User.objects.create_user(email="bob@example.com", password=PASSWORD)


def auth(user):
    return {"Authorization": f"Bearer {AccessToken.for_user(user)}"}


def create_workout(user, name="Push", days_ago=0, activate=True):
    return Workout.objects.create(
        date=timezone.now() - timedelta(days=days_ago),
        user=user,
        activate=activate,
        name=name,
    )


def delete_workout(client, user, workout_pk):
    return client.delete(reverse("workout_delete", args=[workout_pk]), headers=auth(user))


@pytest.mark.django_db
def test_delete_requires_token(client):
    response = client.delete(reverse("workout_delete", args=[1]))

    assert response.status_code == 401


def test_delete_deactivates_own_workout(client, alice):
    workout = create_workout(alice)

    response = delete_workout(client, alice, workout.pk)

    assert response.status_code == 204
    workout.refresh_from_db()
    assert workout.activate is False


def test_deleted_workout_is_no_longer_listed(client, alice):
    create_workout(alice, name="Push")
    pull = create_workout(alice, name="Pull")

    delete_workout(client, alice, pull.pk)
    response = client.get(reverse("workouts_get"), headers=auth(alice))

    assert [workout["name"] for workout in response.json()] == ["Push"]


def test_delete_refuses_other_user_workout(client, alice, bob):
    workout = create_workout(bob)

    response = delete_workout(client, alice, workout.pk)

    assert response.status_code == 404
    workout.refresh_from_db()
    assert workout.activate is True


def test_delete_unknown_workout_returns_404(client, alice):
    response = delete_workout(client, alice, 999999)

    assert response.status_code == 404


def test_delete_keeps_only_the_last_inactive_workouts(client, alice):
    limit = settings.MAX_INACTIVE_WORKOUTS
    # De la plus ancienne à la plus récente, supprimées dans cet ordre.
    workouts = [
        create_workout(alice, name=f"Séance {i}", days_ago=limit - i) for i in range(limit + 1)
    ]

    for workout in workouts:
        delete_workout(client, alice, workout.pk)

    remaining = Workout.objects.filter(user_id=alice, activate=False)
    assert set(remaining.values_list("pk", flat=True)) == {w.pk for w in workouts[1:]}
    assert not Workout.objects.filter(pk=workouts[0].pk).exists()


def test_delete_does_not_purge_other_user_workouts(client, alice, bob):
    limit = settings.MAX_INACTIVE_WORKOUTS
    for i in range(limit):
        create_workout(alice, days_ago=10 + i, activate=False)
        create_workout(bob, days_ago=20 + i, activate=False)
    workout = create_workout(alice)

    delete_workout(client, alice, workout.pk)

    assert Workout.objects.filter(user_id=alice, activate=False).count() == limit
    assert Workout.objects.filter(user_id=bob, activate=False).count() == limit
