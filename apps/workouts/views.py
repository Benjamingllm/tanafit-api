from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from config.settings import MAX_INACTIVE_WORKOUTS

from .models import Workout
from .serializers import WorkoutSerializer


@api_view(["GET"])
def workouts_get(request):
    workouts = Workout.objects.filter(user_id=request.user, activate=True)
    serializer = WorkoutSerializer(workouts, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def workouts_add(request):
    serializer = WorkoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user_id=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
def workouts_update(request, pk):
    workout = get_object_or_404(Workout, pk=pk, user_id=request.user)
    serializer = WorkoutSerializer(workout, request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def workout_delete(request, pk):
    deactivate_workout(request, pk)
    # on récupère les workout du user
    inactive_workouts = Workout.objects.filter(user_id=request.user, activate=False).order_by(
        "-date"
    )
    inactive_workouts = inactive_workouts[MAX_INACTIVE_WORKOUTS:]
    for workout in inactive_workouts:
        workout.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def deactivate_workout(request, pk):
    workout = get_object_or_404(Workout, pk=pk, user_id=request.user)
    workout.activate = False
    workout.save()
