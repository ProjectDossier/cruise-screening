from django.urls import path

from . import views

urlpatterns = [
    path(
        "literature_review/",
        views.literature_review_home,
        name="literature_review_home",
    ),
    path("create_review/", views.create_new_review, name="create_new_review"),
]
