from django.urls import path
from engine import views


urlpatterns = [
    path("start/", views.index, name="index"),
]
