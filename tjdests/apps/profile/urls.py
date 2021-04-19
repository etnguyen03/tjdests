from django.urls import path
from . import views

app_name = "profile"

urlpatterns = [
    path("", views.profile_view, name="index"),
    path("testscore/add", views.TestScoreCreateView.as_view(), name="testscores_add"),
    path("testscore/edit/<int:pk>", views.TestScoreUpdateView.as_view(), name="testscores_edit"),
    path("testscore/delete/<int:pk>", views.TestScoreDeleteView.as_view(), name="testscores_delete"),
    path("decision/add", views.DecisionCreateView.as_view(), name="decision_add"),
    path("decision/edit/<int:pk>", views.DecisionUpdateView.as_view(), name="decision_edit"),
    path("decision/delete/<int:pk>", views.DecisionDeleteView.as_view(), name="decision_delete"),
]