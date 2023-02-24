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
        "literature_review/<int:review_id>/import_papers",
        views.import_papers,
        name="import_papers",
    ),
    path("export_review/<int:review_id>/", views.export_review, name="export_review"),
    path("delete_review/<int:review_id>/", views.delete_review, name="delete_review"),
    path("manage_review/<int:review_id>/", views.manage_review, name="manage_review"),
    path("add_review_member/<int:review_id>", views.add_review_member, name="add_review_member"),
    path("remove_review_member/<int:review_id>", views.remove_review_member, name="remove_review_member"),
    path("create_review/", views.create_new_review, name="create_new_review"),
    path("update_search/<int:review_id>", views.update_search, name="update_search"),
]
