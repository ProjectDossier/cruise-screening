from django.urls import path

from . import views

app_name = "citation_screening"
urlpatterns = [
    path(
        "literature_review/<int:review_id>/automatic_screening",
        views.automatic_screening,
        name="automatic_screening",
    ),
    path(
        "literature_review/<int:review_id>/prompt_based_screening",
        views.prompt_based_screening,
        name="prompt_based_screening",
    ),
    path("screen_papers/<int:review_id>/", views.screen_papers, name="screen_papers"),
    path(
        "screen_paper/<int:review_id>/<str:paper_id>/",
        views.screen_paper,
        name="screen_paper",
    ),
    path("literature_review/<int:review_id>/ditribute_papers", views.distribute_papers, name="distribute_papers"),
]
