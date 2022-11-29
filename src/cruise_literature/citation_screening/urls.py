from django.urls import path

from . import views

app_name = "literature_review"
urlpatterns = [
    path(
        "literature_review/",
        views.literature_review_home,
        name="literature_review_home",
    ),
    path(
        "literature_review/<int:review_id>/",
        views.review_details,
        name="review_details",
    ),
    path(
        "literature_review/<int:review_id>/add_seed_studies",
        views.add_seed_studies,
        name="add_seed_studies",
    ),
    path(
        "literature_review/<int:review_id>/edit",
        views.edit_review,
        name="edit_review",
    ),
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
    path("export_review/<int:review_id>/", views.export_review, name="export_review"),
    path("delete_review/<int:review_id>/", views.delete_review, name="delete_review"),
    path("create_review/", views.create_new_review, name="create_new_review"),

]
