import json
from typing import Dict, Any, Optional

import requests
from django.db import transaction
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
            "http://localhost:8000" + "/question",
            data=json.dumps({"text": query, "model": "default"}),
            headers=headers,
        )
        if res.status_code != 200:
            raise APIException(f"Text-to-text API error: {res.status_code}")
        response = res.json()
        response["status"] = "OK"
        return response
    except requests.exceptions.ConnectionError:
        return {"status": "error", "reason": "Text-to-text API is not available"}


def predict_papers(review: LiteratureReview, paper: Dict[str, Any]) -> Optional[str]:
    if not settings.ML_API:
        return None

    prompt = f"""
    You are a research assistant. You are given a paper and a systematic review.
    Your task is to determine whether the paper is relevant to the review.
    Is the following paper relevant to the review?
    Paper Title: {paper["title"]}
    Paper Abstract: {paper["abstract"]}
    Paper Authors: {paper["authors"]}
    
    Review: {review.title}
    Review abstract: {review.description}
    Please answer with either "yes", "no" or "not sure".
    Do NOT write anything except for one of the three options.
    Select: "yes", "no" or "not sure".
    """
    res = query_text2text_api(prompt)

    return res["response"] if res["status"] == "OK" else None


def prediction_reason(review: LiteratureReview, paper: Dict[str, Any]) -> Optional[str]:
    if not settings.ML_API:
        return None

    prompt = f"""
    You are a research assistant. You are given a paper and a systematic review.
    Your task is to determine whether the paper is relevant to the review.
    Why is the following paper relevant to the review?
    Paper Title: {paper["title"]}
    Paper Abstract: {paper["abstract"]}
    Paper Authors: {paper["authors"]}
    
    Review: {review.title}
    Review abstract: {review.description}
    Please answer with a reason.
    """
    res = query_text2text_api(prompt)

    return res["response"] if res["status"] == "OK" else None


def predict_criterion(
    paper: Dict[str, Any], criterion: list[str, str]
) -> Optional[str]:
    if not settings.ML_API:
        return None

    prompt = f"""
    You are a research assistant. You are given a paper and a systematic review criterion.
    Your task is to determine whether the paper is relevant to the criterion described below.
    If you think the paper is relevant to the criterion, please answer with "yes".
    If you are sure that the paper is not relevant to the criterion, please answer with "no".
    Otherwise, please answer with "not sure".
    Is the following paper relevant to the criterion?
    Paper Title: {paper["title"]}
    Paper Abstract: {paper["abstract"]}
    Paper Authors: {paper["authors"]}
    
    Systematic review criterion: {criterion["text"]}
    Please answer with either "yes", "no" or "not sure". Do NOT write anything except for one of the three options.
    Select: "yes", "no" or "not sure".
    """

    res = query_text2text_api(prompt)

    return res["response"] if res["status"] == "OK" else None


def predict_relevance(review: LiteratureReview, paper: Dict[str, Any]) -> Optional[str]:
    if not settings.ML_API:
        return None

    prompt = f"""
    You are a research assistant. You are given a paper and a systematic review search query.
    Your task is to determine whether the paper is relevant to the query.
    If you think the paper is relevant to the query, please answer with "Highly relevant".
    If you are sure that the paper is not relevant to the query, please answer with "Not relevant".
    Otherwise, please answer with "Somewhat relevant".
    Sometimes, one or more of the elements of the paper description are not available. In this case, you should answer by analysing the rest of the provided data.
    Is the following paper relevant to the queries?
    Paper Title: {paper["title"]}
    Paper Abstract: {paper["abstract"]}
    Paper Authors: {paper["authors"]}
    
    Systematic review search queries: {", ".join(review.search_queries)}

    Please answer with either "Highly relevant", "Somewhat relevant" or "Not relevant". Do NOT write anything except for one of the three options.
    Select: "Highly relevant", "Somewhat relevant" or "Not relevant".
    """

    res = query_text2text_api(prompt)

    return res["response"] if res["status"] == "OK" else None
