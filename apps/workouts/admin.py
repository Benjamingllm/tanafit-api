from django.contrib import admin

from .models import Exercise, MuscleGroup, Set, Template, TemplateExercise, Workout

# Register your models here.
admin.site.register(Template)
admin.site.register(TemplateExercise)
admin.site.register(MuscleGroup)
admin.site.register(Exercise)
admin.site.register(Workout)
admin.site.register(Set)
