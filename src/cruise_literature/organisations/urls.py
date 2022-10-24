from django.urls import path

from . import views

app_name = "organisations"
urlpatterns = [
    path("view_organisations/", views.view_organisations, name="view_organisations"),
    path("create_organisation/", views.create_organisation, name="create_organisation"),
]
