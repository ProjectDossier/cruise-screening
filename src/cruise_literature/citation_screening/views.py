import hashlib
import json
import time
from typing import Dict, List

import rispy
import bibtexparser
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from requests import HTTPError
from django.contrib.auth.decorators import login_required
import datetime

from document_classification.views import (
    predict_papers,
    prediction_reason,
    predict_criterion,
    predict_relevance,
)
from .forms import NewLiteratureReviewForm, EditLiteratureReviewForm
from .models import LiteratureReview
from .process_pdf import parse_doc_grobid
import inspect
from document_classification.registry import MLRegistry
from document_classification.classifiers.dummy import DummyClassifier
from document_classification.classifiers.fasttext_classifier import FastTextClassifier
from django.template.defaulttags import register
from utils.django_tags import first_n_char, first_n_words


MIN_DECISIONS = 1  # TODO replace with database object, review specific


@register.filter
def convert_papers_list(papers, data_format_version):
    """data_format_version 1 and 2 are lists, 3 is a dict"""
    if data_format_version < 3:
        return papers
    else:
        return papers.values()


@login_required
def create_new_review(request):
    initial = {
        "exclusion_criteria": [
            "Paper written in language other than English",
            "Only title is available",
        ]
    }
    if request.method == "POST":
        form = NewLiteratureReviewForm(request.POST, user=request.user, initial=initial)
        if form.is_valid():
            form.save()
            title = form.cleaned_data.get("title")
            messages.success(request, f"New review created: {title}")
            return redirect("home")
        else:
            if "error_messages" in form:
                for msg in form.error_messages:
                    messages.error(request, f"{msg}: {form.error_messages[msg]}")
            elif "errors" in form:
                for msg in form.errors:
                    messages.error(request, f"{msg}: {form.errors[msg]}")

            return render(
                request=request,
                template_name="literature_review/create_literature_review.html",
                context={"form": form},
            )

    form = NewLiteratureReviewForm(user=request.user, initial=initial)
    form.fields["organisation"].queryset = form.fields["organisation"].queryset.filter(
        members=request.user
    )
    return render(
        request=request,
        template_name="literature_review/create_literature_review.html",
        context={"form": form},
    )


def update_criteria(
    current_criteria: Dict[str, List[Dict]],
    inclusion: List[str],
    exclusion: List[str],
    user_id: int,
) -> Dict[str, List[Dict]]:
    """
    Updates the criteria for a literature review. If a criterion is not in the
    current criteria, it is added. If it is in the current criteria but not in the new
    criteria, it is marked as inactive.

    :param current_criteria:
    :param inclusion:
    :param exclusion:
    :param user_id:
    :return:
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    old_inclusion_text = [x["text"] for x in current_criteria["inclusion"]]
    old_exclusion_text = [x["text"] for x in current_criteria["exclusion"]]

    # add new inclusion criteria
    for inc in inclusion:
        if inc in old_inclusion_text:
            continue
        else:
            current_criteria["inclusion"].append(
                {
                    "id": f"in_{len(current_criteria['inclusion'])}",
                    "is_active": True,
                    "text": inc,
                    "comment": "",
                    "added_at": timestamp,
                    "added_by": user_id,
                    "updated_at": timestamp,
                    "updated_by": user_id,
                }
            )

    for exc in exclusion:
        if exc in old_exclusion_text:
            continue
        else:
            current_criteria["exclusion"].append(
                {
                    "id": f"ex_{len(current_criteria['exclusion'])}",
                    "is_active": True,
                    "text": exc,
                    "comment": "",
                    "added_at": timestamp,
                    "added_by": user_id,
                    "updated_at": timestamp,
                    "updated_by": user_id,
                }
            )

    # make is_active False for all criteria that are not in the new list
    for old_inc in old_inclusion_text:
        if old_inc not in inclusion:
            for inc in current_criteria["inclusion"]:
                if inc["text"] == old_inc:
                    inc["is_active"] = False
                    inc["updated_at"] = timestamp
                    inc["updated_by"] = user_id
                    break

    for old_exc in old_exclusion_text:
        if old_exc not in exclusion:
            for exc in current_criteria["exclusion"]:
                if exc["text"] == old_exc:
                    exc["is_active"] = False
                    exc["updated_at"] = timestamp
                    exc["updated_by"] = user_id
                    break

    return current_criteria


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        raise Http404("Review not found")

    if request.method == "POST":
        form = EditLiteratureReviewForm(request.POST, user=request.user)
        if form.is_valid():
            title = form.cleaned_data.get("title")
            review.title = title
            review.description = form.cleaned_data.get("description")
            new_criteria = update_criteria(
                current_criteria=review.criteria,
                inclusion=form.cleaned_data.get("inclusion_criteria"),
                exclusion=form.cleaned_data.get("exclusion_criteria"),
                user_id=request.user.id,
            )
            review.criteria = new_criteria
            review.tags = form.cleaned_data.get("tags")
            review.organisation = form.cleaned_data.get("organisation")
            review.save()
            messages.success(request, f"Review successfully edited: {title}")
            return render(
                request=request,
                template_name="literature_review/view_review.html",
                context={"review": review},
            )
        else:
            if "error_messages" in form:
                for msg in form.error_messages:
                    messages.error(request, f"{msg}: {form.error_messages[msg]}")
            return redirect("home")

    elif request.method == "GET":
        form = EditLiteratureReviewForm(
            user=request.user,
            initial={
                "title": review.title,
                "description": review.description,
                "inclusion_criteria": [
                    x["text"] for x in review.criteria["inclusion"] if x["is_active"]
                ],
                "exclusion_criteria": [
                    x["text"] for x in review.criteria["exclusion"] if x["is_active"]
                ],
                "tags": review.tags,
                "organisation": review.organisation,
            },
        )
        form.fields["organisation"].queryset = form.fields[
            "organisation"
        ].queryset.filter(members=request.user)
        return render(
            request=request,
            template_name="literature_review/edit_literature_review.html",
            context={"form": form, "review": review},
        )


@login_required
def literature_review_home(request):
    context = {
        "literature_reviews": LiteratureReview.objects.filter(members=request.user)
    }

    return render(
        request=request, template_name="literature_review/home.html", context=context
    )


@login_required
def review_details(request, review_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user in review.members.all():
        return render(request, "literature_review/view_review.html", {"review": review})
    else:
        raise Http404("Review not found")


def make_decision(exclusions, inclusions):
    if "yes" in exclusions:
        return False
    if "no" in inclusions:
        return False

    return True


def screen_papers_v2(request, review_id, paper_id=None):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    _papers = review.papers
    if request.method == "GET":
        if paper_id:
            edited_index = [
                index_i
                for index_i, x in enumerate(_papers)
                if str(x["id"]) == str(paper_id)
            ][0]
            return render(
                request,
                "literature_review/screen_paper.html",
                {
                    "review": review,
                    "paper": _papers[edited_index],
                    "start_time": time.time(),
                },
            )

        for paper in _papers:
            if (
                not paper.get("decisions")
                or len(paper.get("decisions")) < MIN_DECISIONS
            ):
                return render(
                    request,
                    "literature_review/screen_paper.html",
                    {"review": review, "paper": paper, "start_time": time.time()},
                )
    elif request.method == "POST":
        screening_time = round(time.time() - float(request.POST["start_time"]), 2)
        keys = request.POST.keys()
        exclusions = [request.POST[x] for x in keys if x.startswith("exclusion")]
        inclusions = [request.POST[x] for x in keys if x.startswith("inclusion")]

        paper_id = request.POST["paper_id"]
        reason = request.POST["reason"]
        eligibility_decision = make_decision(
            exclusions=exclusions, inclusions=inclusions
        )
        topic_relevance = request.POST["topic_relevance"]
        domain_relevance = request.POST["domain_relevance"]
        decision = request.POST["decision"]
        paper_prior_knowledge = request.POST["paper_prior_knowledge"]
        authors_prior_knowledge = request.POST["authors_prior_knowledge"]

        edited_index = [
            index_i
            for index_i, x in enumerate(_papers)
            if str(x["id"]) == str(paper_id)
        ][
            0
        ]  # FIXME: this will fail if duplicates in DB
        _papers[edited_index]["decisions"] = [
            {
                "reviewer_id": request.user.pk,
                "decision": int(decision),
                "eligibility_decision": eligibility_decision,
                "reason": reason,
                "inclusions": inclusions,
                "exclusions": exclusions,
                "stage": "title_abstract",
                "domain_relevance": int(domain_relevance),
                "topic_relevance": int(topic_relevance),
                "paper_prior_knowledge": int(paper_prior_knowledge),
                "authors_prior_knowledge": int(authors_prior_knowledge),
                "screening_time": screening_time,
            }
        ]
        _papers[edited_index]["decision"] = decision
        if len(_papers[edited_index]["decisions"]) >= MIN_DECISIONS:
            _papers[edited_index]["screened"] = True
        review.save()

        for paper in _papers:
            if (
                not paper.get("decisions")
                or len(paper.get("decisions")) < MIN_DECISIONS
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
            else:
                return render(
                    request, "literature_review/view_review.html", {"review": review}
                )


@login_required
def screen_papers(request, review_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        raise Http404("Review not found")

    if review.data_format_version < 3:
        return screen_papers_v2(request, review_id, None)
    else:
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
            return render(
                request, "literature_review/view_review.html", {"review": review}
            )


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

    _papers = list(review.papers.values())
    if request.method == "GET":
        return render(
            request,
            "literature_review/screen_paper.html",
            {
                "review": review,
                "paper": review.papers[paper_id],
                "start_time": time.time(),
            },
        )
    if request.method == "POST":

        paper_id = request.POST["paper_id"]
        review, request = create_screening_decisions(request, review, paper_id)
        review.save()

        return redirect("literature_review:view_review", review_id=review_id)


@login_required
def export_review(request, review_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        raise Http404("Review not found")
    data = {
        "review_id": review.id,
        "title": review.title,
        "description": review.description,
        "search_queries": review.search_queries,
        "criteria": review.criteria,
        "papers": review.papers,
    }
    return HttpResponse(json.dumps(data, indent=2), content_type="application/json")


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.filter(
        om_through__member=request.user, om_through__role="AD"
    ):
        return redirect("literature_review:review_details", review_id=review_id)
    review.delete()
    return redirect("literature_review:literature_review_home")


def import_ris(file_data):
    """loads RIS file data into a list of papers"""
    file_data = "\n".join([line.strip() for line in file_data.splitlines()])
    entries = rispy.loads(file_data, skip_unknown_tags=True)
    papers = []
    for entry in entries:
        paper = {}
        paper['title'] = entry.get("title")
        paper['abstract'] = entry.get("abstract")
        paper['authors'] = ", ".join(entry.get("authors"))
        paper['venue'] = entry.get("journal_name")
        paper['publication_date'] = entry.get("year")
        paper['doi'] = entry.get("doi")
        paper['url'] = entry.get("url")
        if paper['url'] is None:
            paper['url'] = f"https://www.doi.org/{paper['doi']}"
        paper['keywords'] = entry.get("keywords")
        paper['pdf'] = entry.get("pdf")
        paper['id'] = entry.get("id")

        if paper['id'] is None:
            paper['id'] = hashlib.md5(paper['title'].encode('utf-8')).hexdigest()
        papers.append(paper)

    return papers


def import_bib(file_data):
    bib_database = []
    for entry in bibtexparser.loads(file_data).entries:
        keywords = []
        if entry.get("keywords"):
            keywords = entry.get("keywords").split(",")
        paper = {
            "id": entry["ID"],
            "title": entry.get("title"),
            "authors": entry.get("author"),
            "publication_date": entry.get("year"),
            "abstract": entry.get("abstract"),
            "venue": entry.get("journal"),
            "doi": entry.get("doi"),
            "pdf": entry.get("pdf"),
            "url": entry.get("url"),
            "keywords_snippet": keywords,
            "notes": entry.get("note"),
            "other_fields": entry,
            "decisions": [],
            "decision": None,
            "screened": False,
            "included": False,
        }
        bib_database.append(paper)
    return bib_database


def import_json(file_data):
    pass


def import_papers(request, review_id):
    """Import papers from a file.
    Supported file types: RIS, bib and json.

    :param request: HTTP request
    :type request: HttpRequest
    :param review_id: Literature review ID
    :type review_id: int
    :return: redirect to the view review page
    :rtype: HttpResponse
    """
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        raise Http404("Review not found")
    if request.method == "POST":
        file = request.FILES["bibliography_file"]
        file_data = file.read().decode("utf-8")
        if file:
            search_origin = {
                "origin": "file_import",
                "search_engine": "file_import",
                "query": file.name,
                "added_at": str(datetime.datetime.now()),
                "added_by": request.user.username,
            }
            _papers = []
            if file.name.endswith(".ris"):
                _papers = import_ris(file_data)
            elif file.name.endswith(".bib"):
                _papers = import_bib(file_data)
            elif file.name.endswith(".json"):
                import_json(file_data)
            else:
                raise Http404("Invalid file type")

            for paper in _papers:
                if paper["id"] in review.papers:
                    continue

                paper["search_origin"] = [search_origin]
                paper["search_origin"][0]["paper_id"] = paper["id"]
                review.papers[paper["id"]] = paper
                review.save()

            return render(
                request=request,
                template_name="literature_review/view_review.html",
                context={"review": review},
            )
    else:
        return render(
            request, "literature_review/import_papers.html", {"review": review}
        )


@login_required
def add_seed_studies(request, review_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        raise Http404("Review not found")

    if request.method == "GET":
        return render(
            request,
            "literature_review/add_seed_studies.html",
            {"review": review},
        )
    elif request.method == "POST":
        seed_studies_urls = request.POST["seed_studies_urls"]
        seed_studies_urls = list(
            set([x.strip() for x in seed_studies_urls.split("\n")])
        )

        added_studies = []
        for seed_studies_url in seed_studies_urls:
            if not seed_studies_url.strip():
                continue

            try:
                doc = parse_doc_grobid(url=seed_studies_url)
                # print(doc.header.title)
                # new_papers = list(review.papers)
                _new_papers = {
                    "id": doc.pdf_md5,
                    "pdf": seed_studies_url,
                    "url": doc.header.url,
                    "title": doc.header.title,
                    "abstract": doc.abstract,
                    "snippet": doc.abstract[:300],
                    "authors": ", ".join([a.full_name for a in doc.header.authors]),
                    "venue": doc.header.journal,
                    "publication_date": doc.header.date,
                    "n_references": len(doc.citations),  # TODO: change to n_references
                    "n_citations": None,
                    "core_id": None,
                    "semantic_scholar_id": None,
                    "query": None,
                    "search_engine": "Seed Study",
                    "decision": None,
                    "seed_study": True,
                }
                # )
                review.papers[doc.pdf_md5] = _new_papers
                review.save()
                added_studies.append(seed_studies_url)
            except HTTPError:
                print("HTTPError")

        if added_studies:
            messages.success(
                request,
                f"{len(added_studies)} new seed studies added: {', '.join(added_studies)}",
            )

        return render(
            request,
            "literature_review/add_seed_studies.html",
            {"review": review},
        )


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
