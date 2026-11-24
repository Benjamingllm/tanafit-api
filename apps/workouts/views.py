from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Workout
from .serializers import WorkoutSerializer


@api_view(["GET"])
def workouts_get(request):
    workouts = Workout.objects.filter(user_id=request.user)
    serializer = WorkoutSerializer(workouts, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def workouts_add(request):
    serializer = WorkoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user_id=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
