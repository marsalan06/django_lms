from django.contrib import admin
from django.contrib.auth.models import Group

from .models import TakenCourse, Result


class ScoreAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "course",
        "total",
        "grade",
        "comment",
        "avg_total",
        "final_grade",
        "final_comment",
    ]


class ResultAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "session",
        "semesters",
        "final_avg_total",
        "final_grade",
        "final_comment",
    ]


admin.site.register(TakenCourse, ScoreAdmin)
admin.site.register(Result, ResultAdmin)
