from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("index", views.home, name="home1"),
    path("about/", views.about, name="about"),
]
