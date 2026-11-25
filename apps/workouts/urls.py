from django.urls import path

from .views import workout_delete, workouts_add, workouts_get, workouts_update

urlpatterns = [
    path("workouts_get/", workouts_get, name="workouts_get"),
    path("workouts_add/", workouts_add, name="workouts_add"),
    path("workouts_update/<int:pk>/", workouts_update, name="workouts_update"),
    path("workout_delete/<int:pk>/", workout_delete, name="workout_delete"),
]
