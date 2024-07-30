from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path("<slug>/quizzes/", quiz_list, name="quiz_index"),
    path("progress/", view=QuizUserProgressView.as_view(), name="quiz_progress"),
    # path('marking/<int:pk>/', view=QuizMarkingList.as_view(), name='quiz_marking'),
    path("marking_list/", view=QuizMarkingList.as_view(), name="quiz_marking"),
    path(
        "marking/<int:pk>/",
        view=QuizMarkingDetail.as_view(),
        name="quiz_marking_detail",
    ),
    path("<int:pk>/<slug>/take/", view=QuizTake.as_view(), name="quiz_take"),
    path("<slug>/quiz_add/", QuizCreateView.as_view(), name="quiz_create"),
    path("<slug>/<int:pk>/add/", QuizUpdateView.as_view(), name="quiz_update"),
    path("<slug>/<int:pk>/delete/", quiz_delete, name="quiz_delete"),
    path(
        "mc-question/add/<slug>/<int:quiz_id>/",
        MCQuestionCreate.as_view(),
        name="mc_create",
    ),
    path(
        "mc-question/edit/<slug>/<int:quiz_id>/<int:pk>/",
        MCQuestionEdit.as_view(),
        name="mc_edit",
    ),
    path(
        "desc-question/add/<str:slug>/<int:quiz_id>/",
        add_descriptive_question,
        name="add_descriptive_question",
    ),
    path(
        "questions/",
        DescriptiveQuestionListView.as_view(),
        name="descriptive_question_list",
    ),
    path(
        "questions/<int:pk>/",
        DescriptiveQuestionDetailView.as_view(),
        name="descriptive_question_detail",
    ),
    path(
        "<slug:slug>/descriptive-question/add/<int:quiz_id>/",
        DescriptiveQuestionCreate.as_view(),
        name="descriptive_create",
    ),
    # path('mc-question/add/<int:pk>/<quiz_pk>/', MCQuestionCreate.as_view(), name='mc_create'),
]
