from django.urls import path

from . import views

urlpatterns = [
    path("create_review/", views.create_new_review, name="create_new_review"),
]
