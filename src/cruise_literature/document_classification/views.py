import json
from typing import Dict, Any, Optional

import requests
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.exceptions import APIException

from literature_review.models import LiteratureReview
from cruise_literature import settings
from .models import Endpoint
from .models import MLAlgorithm
from .models import MLAlgorithmStatus
from .models import MLRequest
from .serializers import EndpointSerializer
from .serializers import MLAlgorithmSerializer
from .serializers import MLAlgorithmStatusSerializer
from .serializers import MLRequestSerializer


class EndpointViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = EndpointSerializer
    queryset = Endpoint.objects.all()


class MLAlgorithmViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = MLAlgorithmSerializer
    queryset = MLAlgorithm.objects.all()


def deactivate_other_statuses(instance):
    old_statuses = MLAlgorithmStatus.objects.filter(
        parent_mlalgorithm=instance.parent_mlalgorithm,
        created_at__lt=instance.created_at,
        active=True,
    )
    for i in range(len(old_statuses)):
        old_statuses[i].active = False
    MLAlgorithmStatus.objects.bulk_update(old_statuses, ["active"])


class MLAlgorithmStatusViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
):
    serializer_class = MLAlgorithmStatusSerializer
    queryset = MLAlgorithmStatus.objects.all()

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                instance = serializer.save(active=True)
                # set active=False for other statuses
                deactivate_other_statuses(instance)

        except Exception as e:
            raise APIException(str(e)) from e


class MLRequestViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin,
):
    serializer_class = MLRequestSerializer
    queryset = MLRequest.objects.all()


def query_text2text_api(query: str) -> Dict[str, Any]:
    headers = {"Content-type": "application/json"}
    try:
        res = requests.post(
            "http://localhost:5000" + "/question",
            data=json.dumps({"text": query}),
            headers=headers,
        )
        return res.json()
    except requests.exceptions.ConnectionError:
        return {"status": "error", "reason": "Text-to-text API is not available"}


def predict_papers(review: LiteratureReview, paper: Dict[str, Any]) -> Optional[str]:
    if not settings.TEXT_TO_TEXT_API:
        return None

    prompt = f"""
    Is the following paper relevant to the review?
    Paper Title: {paper['title']}
    Paper Abstract: {paper['abstract']}
    Paper Authors: {paper['authors']}
    
    Review: {review.title}
    Review abstract: {review.description}
    Please answer with either "yes", "no" or "not sure".
    """
    res = query_text2text_api(prompt)

    return res["response"] if res["status"] == "OK" else None


def prediction_reason(review: LiteratureReview, paper: Dict[str, Any]) -> Optional[str]:
    if not settings.TEXT_TO_TEXT_API:
        return None

    prompt = f"""
    Why is the following paper relevant to the review?
    Paper Title: {paper['title']}
    Paper Abstract: {paper['abstract']}
    Paper Authors: {paper['authors']}
    
    Review: {review.title}
    Review abstract: {review.description}
    Please answer with a reason.
    """
    res = query_text2text_api(prompt)

    return res["response"] if res["status"] == "OK" else None


def predict_criterion(paper: Dict[str, Any], criterion: [str, str]) -> Optional[str]:
    if not settings.TEXT_TO_TEXT_API:
        return None

    prompt = f"""
    Is the following paper relevant to the criterion?
    Paper Title: {paper['title']}
    Paper Abstract: {paper['abstract']}
    Paper Authors: {paper['authors']}
    
    Criterion: {criterion['text']}
    Please answer with either "yes", "no" or "not sure".
    """
    res = query_text2text_api(prompt)

    return res["response"] if res["status"] == "OK" else None


def predict_relevance(review: LiteratureReview, paper: Dict[str, Any]) -> Optional[str]:
    if not settings.TEXT_TO_TEXT_API:
        return None

    prompt = f"""
    Is the following paper relevant to the queries?
    Paper Title: {paper['title']}
    Paper Abstract: {paper['abstract']}
    Paper Authors: {paper['authors']}
    
    Review search queries: {', '.join(review.search_queries)}

    Please answer with either "Highly relevant", "Somewhat relevant" or "Not relevant".
    """
    res = query_text2text_api(prompt)

    return res["response"] if res["status"] == "OK" else None
