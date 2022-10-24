from django.urls import path

from . import views

app_name = "organisations"
urlpatterns = [
    path("view_all_organisations/", views.view_all_organisations, name="view_all_organisations"),
    path("view_organisation/<int:organisation_id>/", views.view_organisation, name="view_organisation"),
    path("view_organisation/<int:organisation_id>/add_member/", views.add_member, name="add_member"),
    path("view_organisation/<int:organisation_id>/remove_member/", views.remove_member, name="remove_member"),
    path("create_organisation/", views.create_organisation, name="create_organisation"),
]
