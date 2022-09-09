from django.urls import path

from . import views

urlpatterns = [
    path(r"search_concepts/<query>/", views.search_concepts, name="search_concepts"),
    path(r"classify_concepts/<title>/", views.classify_concepts, name="classify_concepts"),
]
