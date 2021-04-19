from django.urls import path
from . import views

app_name = "destinations"

urlpatterns = [
    path("", views.StudentDestinationListView.as_view(), name="students"),
    path("colleges", views.CollegeDestinationListView.as_view(), name="colleges"),
]