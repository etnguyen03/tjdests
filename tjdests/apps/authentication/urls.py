from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "authentication"

urlpatterns = [
    path("", views.index_view, name="index"),
    path("login", views.LoginViewCustom.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("tos", views.accept_tos_view, name="tos"),
]
