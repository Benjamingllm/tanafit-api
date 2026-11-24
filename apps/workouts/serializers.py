from django.db import transaction
from rest_framework import serializers

from .models import Exercise, Set, Workout


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = "__all__"


class SetSerializer(serializers.ModelSerializer):
    exercise_name = ExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = Set
        fields = "__all__"
        read_only_fields = ["workout"]


class WorkoutSerializer(serializers.ModelSerializer):
    sets = SetSerializer(many=True)

    class Meta:
        model = Workout
        exclude = ["user_id"]

    def create(self, data):
        sets = data.pop("sets", [])
        workout = Workout.objects.create(**data)
        with transaction.atomic():
            for set in sets:
                Set.objects.create(workout=workout, **set)
        return workout
