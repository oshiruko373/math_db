# problems/admin.py
from django.contrib import admin
from .models import Problem, ThoughtProcess, Tag

admin.site.register(Problem)
admin.site.register(ThoughtProcess)
admin.site.register(Tag)