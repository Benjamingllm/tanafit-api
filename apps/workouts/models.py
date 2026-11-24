from django.db import models

from apps.users.models import User

# Create your models here.


class MuscleGroup(models.Model):
    name = models.CharField("name")

    def __str__(self):
        return self.name


class Exercise(models.Model):
    name = models.CharField("name")
    muscle_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Template(models.Model):
    name = models.CharField("name")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Workout(models.Model):
    date = models.DateTimeField("Date")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(Template, null=True, blank=True, on_delete=models.CASCADE)
    activate = models.BooleanField("activated")

    def __str__(self):
        return self.name


class TemplateExercise(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    set_amount = models.IntegerField("set_amount")
    min_rep_amount = models.IntegerField("min_rep_amount")
    max_rep_amount = models.IntegerField("max_rep_amount")

    def __str__(self):
        return self.name


class Set(models.Model):
    reps = models.IntegerField("reps")
    wheight = models.FloatField("wheight")
    is_warmup = models.BooleanField("is_warmup", default=True)
    charge_index = models.IntegerField("wharge_index")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
