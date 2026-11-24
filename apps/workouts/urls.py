from django.urls import path

from .views import workouts_add, workouts_get

urlpatterns = [
    path("workouts-get/", workouts_get, name="workouts-get"),
    path("workouts-add/", workouts_add, name="workouts-add"),
]
