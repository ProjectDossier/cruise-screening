from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("index", views.home, name="index"),
    path("about/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
]
