import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User
from apps.workouts.models import Exercise, MuscleGroup, Set, Template, TemplateExercise, Workout

PASSWORD = "motdepasse-test-1"


@pytest.fixture
def alice(db):
    return User.objects.create_user(email="alice@example.com", password=PASSWORD)


@pytest.fixture
def bob(db):
    return User.objects.create_user(email="bob@example.com", password=PASSWORD)


@pytest.fixture
def bench_press(db):
    chest = MuscleGroup.objects.create(name="Pectoraux")
    return Exercise.objects.create(name="Développé couché", muscle_group=chest)


def auth(user):
    return {"Authorization": f"Bearer {AccessToken.for_user(user)}"}


def create_workout(user, name="Push"):
    return Workout.objects.create(date=timezone.now(), user_id=user, activate=True, name=name)


@pytest.mark.django_db
def test_workouts_requires_token(client):
    response = client.get(reverse("workouts_get"))

    assert response.status_code == 401


def test_workouts_returns_empty_list_without_workouts(client, alice):
    response = client.get(reverse("workouts_get"), headers=auth(alice))

    assert response.status_code == 200
    assert response.json() == []


def test_workouts_returns_only_own_workouts(client, alice, bob):
    create_workout(alice, name="Push")
    create_workout(bob, name="Pull")

    response = client.get(reverse("workouts_get"), headers=auth(alice))

    assert response.status_code == 200
    assert [workout["name"] for workout in response.json()] == ["Push"]


def test_workout_includes_its_sets(client, alice, bench_press):
    push = create_workout(alice, name="Push")
    create_workout(alice, name="Pull")
    Set.objects.create(reps=10, wheight=40.0, charge_index=3, exercise=bench_press, workout=push)
    Set.objects.create(
        reps=8, wheight=60.0, charge_index=2, is_warmup=False, exercise=bench_press, workout=push
    )

    response = client.get(reverse("workouts_get"), headers=auth(alice))

    workouts = {workout["name"]: workout for workout in response.json()}
    assert sorted(s["reps"] for s in workouts["Push"]["sets"]) == [8, 10]
    assert workouts["Pull"]["sets"] == []


def test_models_display_their_name(alice, bench_press):
    template = Template.objects.create(name="Haut du corps", user=alice)
    template_exercise = TemplateExercise.objects.create(
        template=template,
        exercise=bench_press,
        set_amount=4,
        min_rep_amount=6,
        max_rep_amount=10,
    )

    assert str(bench_press.muscle_group) == "Pectoraux"
    assert str(bench_press) == "Développé couché"
    assert str(template) == "Haut du corps"
    assert str(template_exercise) == "Développé couché"
    assert str(create_workout(alice, name="Push")) == "Push"


def patch_workout(client, user, workout, data):
    return client.patch(
        reverse("workouts_update", args=[workout.pk]),
        data=data,
        content_type="application/json",
        headers=auth(user),
    )


def test_update_changes_own_workout(client, alice):
    workout = create_workout(alice, name="Push")

    response = patch_workout(client, alice, workout, {"name": "Push lourd"})

    assert response.status_code == 200
    assert response.json()["name"] == "Push lourd"
    workout.refresh_from_db()
    assert workout.name == "Push lourd"
    assert workout.activate is True


def test_update_refuses_other_user_workout(client, alice, bob):
    workout = create_workout(bob, name="Pull")

    response = patch_workout(client, alice, workout, {"name": "Piraté"})

    assert response.status_code == 404
    workout.refresh_from_db()
    assert workout.name == "Pull"


def test_update_cannot_change_owner(client, alice, bob):
    workout = create_workout(alice)

    response = patch_workout(client, alice, workout, {"user_id": bob.pk})

    assert response.status_code == 200
    workout.refresh_from_db()
    assert workout.user_id == alice
