from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from django.urls import path

from document_classification.views import (
    EndpointViewSet,
    MLAlgorithmViewSet,
    MLAlgorithmStatusViewSet,
    MLRequestViewSet,
)


app_name = "document_classification"

router = DefaultRouter(trailing_slash=False)
router.register(r"endpoints", EndpointViewSet, basename="endpoints")
router.register(r"mlalgorithms", MLAlgorithmViewSet, basename="mlalgorithms")
router.register(
    r"mlalgorithmstatuses", MLAlgorithmStatusViewSet, basename="mlalgorithmstatuses"
)
router.register(r"mlrequests", MLRequestViewSet, basename="mlrequests")

urlpatterns = [
    path(r"api/v1/", include((router.urls, app_name))),
    ]
