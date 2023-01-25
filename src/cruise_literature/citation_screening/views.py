import time
from typing import Optional

import numpy as np
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import datetime

from document_classification.views import (
    predict_papers,
    prediction_reason,
    predict_criterion,
    predict_relevance,
)
from literature_review.models import LiteratureReview
import inspect
from document_classification.registry import MLRegistry
from document_classification.classifiers.dummy import DummyClassifier
from document_classification.classifiers.fasttext_classifier import FastTextClassifier
from .models import CitationScreening


def _distribute_papers_for_reviewers(
    papers: list[str],
    members: list[str],
    min_decisions: int,
    papers_per_member: Optional[dict[str, int]] = None,
) -> dict[str, dict[str, str]]:
    """Distribute papers to review members for screening

    :param papers: list of paper IDs in the review
    :param members: list of member usernames
    :param min_decisions: minimum decisions per paper
    :param papers_per_member: optional dictionary parameter with number of papers per member.
    If None, then every member gets equal number of papers for screening
    :return: dict with tasks for each member
    """
    if len(members) < min_decisions:
        raise ValueError(
            "Number of members should be greater or equal to min_decisions"
        )
    if not members:
        raise ValueError("Number of members should be greater than 0")

    if papers_per_member is None:
        _total = len(papers) * min_decisions
        papers_per_member = {member: (_total // len(members)) + 1 for member in members}
    tasks = {member: [] for member in members}

    for paper in papers:
        for member in np.random.choice(
            members,
            min_decisions,
            replace=False,
            p=np.array(list(papers_per_member.values()))
            / sum(papers_per_member.values()),
        ):
            if papers_per_member[member] > 0:
                tasks[member].append(paper)
                papers_per_member[member] -= 1
    return tasks


@login_required
def distribute_papers(request, review_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        raise Http404("Review not found")

    # check if ready for screening

    if request.method == "GET":
        screenings = CitationScreening.objects.filter(literature_review=review).all()
        if screenings:
            # todo: check for last date and re-run only if there are new papers not in tasks.
            return redirect("literature_review:review_details", review_id=review.id)
        else:
            tasks = _distribute_papers_for_reviewers(
                papers=list(review.papers.keys()),
                members=list(review.members.all().values_list("username", flat=True)),
                min_decisions=review.min_decisions,
            )
            # create new screening object
            screening = CitationScreening.objects.create(
                literature_review=review,
                tasks=tasks,
                screening_level=1  # title and abstract screening level
                # todo: add papers_updated at
            )
            screening.save()
            return redirect("literature_review:review_details", review_id=review.id)


def make_decision(exclusions, inclusions):
    if "yes" in exclusions:
        return False
    if "no" in inclusions:
        return False

    return True


@login_required
def screen_papers(request, review_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        raise Http404("Review not found")

    _papers = list(review.papers.values())
    if request.method == "GET":
        for paper in _papers:
            if (
                not paper.get("decisions")
                or len(paper.get("decisions")) < review.min_decisions
            ):
                return render(
                    request,
                    "literature_review/screen_paper.html",
                    {"review": review, "paper": paper, "start_time": time.time()},
                )
    elif request.method == "POST":

        paper_id = request.POST["paper_id"]
        review, request = create_screening_decisions(request, review, paper_id)
        review.save()

        for paper in _papers:
            if (
                not paper.get("decisions")
                or len(paper.get("decisions")) < review.min_decisions
            ):
                return render(
                    request,
                    "literature_review/screen_paper.html",
                    {
                        "review": review,
                        "paper": paper,
                        "start_time": time.time(),
                    },
                )
        return render(request, "literature_review/view_review.html", {"review": review})


def create_screening_decisions(request, review, paper_id):
    screening_time = round(time.time() - float(request.POST["start_time"]), 2)

    # todo: add option in the review to make inclusion/exclusion mandatory or not
    inclusion_decisions = {
        inc_crit["id"]: request.POST.get(inc_crit["id"], False)
        for inc_crit in review.criteria["inclusion"]
        if inc_crit["is_active"]
    }
    exclusion_decisions = {
        exc_crit["id"]: request.POST.get(exc_crit["id"], False)
        for exc_crit in review.criteria["exclusion"]
        if exc_crit["is_active"]
    }

    reason = request.POST["reason"]
    topic_relevance = request.POST["topic_relevance"]
    domain_relevance = request.POST["domain_relevance"]
    decision = request.POST["decision"]
    paper_prior_knowledge = request.POST["paper_prior_knowledge"]
    authors_prior_knowledge = request.POST["authors_prior_knowledge"]

    review.papers[paper_id]["decisions"] = [
        {
            "reviewer_id": request.user.pk,
            "decision": int(decision),
            "reason": reason,
            "exclusion_decisions": exclusion_decisions,
            "inclusion_decisions": inclusion_decisions,
            "stage": "title_abstract",
            "domain_relevance": int(domain_relevance),
            "topic_relevance": int(topic_relevance),
            "paper_prior_knowledge": int(paper_prior_knowledge),
            "authors_prior_knowledge": int(authors_prior_knowledge),
            "screening_time": screening_time,
        }
    ]
    review.papers[paper_id]["decision"] = decision
    if len(review.papers[paper_id]["decisions"]) >= review.min_decisions:
        review.papers[paper_id]["screened"] = True

    return review, request


@login_required
def screen_paper(request, review_id, paper_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        raise Http404("Review not found")

    if review.data_format_version < 3:
        raise Http404("Review not found")

    if request.method == "GET":
        paper = review.papers[paper_id]
        if paper.get("decisions"):
            paper_decisions = [
                x for x in paper["decisions"] if x["reviewer_id"] == request.user.pk
            ]
            if paper_decisions:
                paper_decision = paper_decisions[0]
                return render(
                    request,
                    "literature_review/screen_paper.html",
                    {
                        "review": review,
                        "paper": paper,
                        "paper_decision": paper_decision,
                        "start_time": time.time(),
                    },
                )
        return render(
            request,
            "literature_review/screen_paper.html",
            {
                "review": review,
                "paper": paper,
                "start_time": time.time(),
            },
        )
    if request.method == "POST":

        paper_id = request.POST["paper_id"]
        review, request = create_screening_decisions(request, review, paper_id)
        review.save()

        return redirect("literature_review:view_review", review_id=review_id)


@login_required
def automatic_screening(request, review_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        raise Http404("Review not found")

    if request.method == "GET":
        try:
            registry = MLRegistry()  # create ML registry
            # add to ML registry
            registry.add_algorithm(
                endpoint_name=review.id,
                algorithm_object=DummyClassifier(),
                algorithm_name="dummy classifier",
                algorithm_status="production",
                algorithm_version="0.0.1",
                owner=request.user,
                algorithm_description="Dummy classifier always predicting '1'.",
                algorithm_code=inspect.getsource(DummyClassifier),
            )
        except Exception as e:
            print("Exception while loading the algorithms to the registry,", e)

        xy_train = {}
        x_pred = {}
        for key, paper in review.papers:
            if paper.get("decisions") and paper.get("screened"):
                decision = paper["decisions"][0]["decision"]
                if decision == "-1":
                    decision = "1"
                xy_train[paper["id"]] = {
                    "title": f'{paper["title"]} {paper["abstract"]}',
                    "decision": decision,
                }  # TODO: convert -1 (maybe) to 1
            else:
                x_pred[paper["id"]] = {"title": f'{paper["title"]} {paper["abstract"]}'}
        algorithm_object = FastTextClassifier()
        # algorithm_object = DummyClassifier()
        algorithm_object.train(
            input_data=[x["title"] for x in xy_train.values()],
            true_labels=[x["decision"] for x in xy_train.values()],
        )
        y_pred = algorithm_object.predict([x["title"] for x in x_pred.values()])
        print(y_pred)

        if y_pred["status"] == "OK":
            for paper_id, predicted_label in zip(x_pred.keys(), y_pred["predictions"]):
                edited_index = [
                    index_i
                    for index_i, x in enumerate(review.papers)
                    if str(x["id"]) == str(paper_id)
                ][0]
                review.papers[edited_index]["automatic_decisions"] = {
                    "algorithm_id": str(algorithm_object),
                    "decision": predicted_label["label"],
                    "probability": float(predicted_label["probability"]),
                    "time": str(datetime.datetime.now()),
                }

                review.save()
        return render(
            request=request,
            template_name="literature_review/view_review.html",
            context={"review": review},
        )


def get_decisions(paper, decision_type: str):
    """Get decisions forŁ a paper."""
    # todo: if there are already decisions from the same user, return the newest one
    if decision_type == "automatic":
        return paper.get("automatic_decisions")
    elif decision_type == "manual":
        return paper.get("decisions")
    else:
        raise ValueError("decision_type must be 'automatic' or 'manual'")


def prompt_based_screening(request, review_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        raise Http404("Review not found")

    model_id = "T0_3B"
    for paper_id, paper in review.papers.items():
        if not review.papers[paper_id].get("automatic_decisions"):
            review.papers[paper_id]["automatic_decisions"] = []

        if review.papers[paper_id]["automatic_decisions"]:
            already_reviewed = [
                _dec
                for _dec in review.papers[paper_id]["automatic_decisions"]
                if _dec["reviewer_id"] == model_id
            ]
            if already_reviewed:
                continue

        start_time = time.time()
        if prediction_result := predict_papers(review, paper):
            inclusion_decisions = {
                criterion["id"]: predict_criterion(paper, criterion).lower()
                for criterion in review.criteria["inclusion"]
                if criterion["is_active"]
            }

            exclusion_decisions = {
                criterion["id"]: predict_criterion(paper, criterion).lower()
                for criterion in review.criteria["exclusion"]
                if criterion["is_active"]
            }

            _prediction_reason = prediction_reason(review, paper)
            topic_relevance = predict_relevance(review, paper)

            review.papers[paper_id]["automatic_decisions"].append(
                {
                    "reviewer_id": model_id,
                    "decision": prediction_result.lower(),
                    "reason": _prediction_reason,
                    "exclusion_decisions": exclusion_decisions,
                    "inclusion_decisions": inclusion_decisions,
                    "stage": "title_abstract",
                    # "domain_relevance": domain_relevance,
                    "topic_relevance": topic_relevance,
                    "paper_prior_knowledge": None,
                    "authors_prior_knowledge": None,
                    "screening_time": time.time() - start_time,
                    "added_at": str(datetime.datetime.now()),
                    "added_by": request.user.username,
                }
            )
            review.save()

    return render(
        request=request,
        template_name="literature_review/view_review.html",
        context={"review": review},
    )
