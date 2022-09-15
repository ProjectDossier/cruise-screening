import json
import time

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from requests import HTTPError

from .forms import NewLiteratureReviewForm, EditLiteratureReviewForm
from .models import LiteratureReview
from .process_pdf import parse_doc_grobid

MIN_DECISIONS = 1  # TODO replace with database object, review specific


def create_new_review(request):
    initial = {
        "exclusion_criteria": ["Paper written in language other than English", "Only title is available"]}
    if request.method == "POST":
        form = NewLiteratureReviewForm(request.POST, user=request.user, initial=initial)
        if form.is_valid():
            form.save()
            title = form.cleaned_data.get("title")
            messages.success(request, f"New review created: {title}")
            return redirect("home")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

            return render(
                request=request,
                template_name="literature_review/create_literature_review.html",
                context={"form": form},
            )

    if not request.user.is_authenticated:
        return redirect("home")

    form = NewLiteratureReviewForm(user=request.user, initial=initial)
    return render(
        request=request,
        template_name="literature_review/create_literature_review.html",
        context={"form": form},
    )


def edit_review(request, review_id):
    if not request.user.is_authenticated:
        return redirect("home")

    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        return redirect("home")

    if request.method == "POST":
        form = EditLiteratureReviewForm(request.POST, user=request.user)
        if form.is_valid():
            # form.save()
            title = form.cleaned_data.get("title")
            review.title = title
            review.description = form.cleaned_data.get("description")
            review.inclusion_criteria = form.cleaned_data.get("inclusion_criteria")
            review.exclusion_criteria = form.cleaned_data.get("exclusion_criteria")
            review.tags = form.cleaned_data.get("tags")
            review.save()
            messages.success(request, f"Review successfully edited: {title}")
            return render(
                request=request,
                template_name="literature_review/view_review.html",
                context={"review": review},
            )
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
            return redirect("home")

    elif request.method == "GET":
        form = EditLiteratureReviewForm(
            user=request.user,
            initial={
                "title": review.title,
                "description": review.description,
                "inclusion_criteria": review.inclusion_criteria,
                "exclusion_criteria": review.exclusion_criteria,
                "tags": review.tags,
            },
        )
        return render(
            request=request,
            template_name="literature_review/edit_literature_review.html",
            context={"form": form, "review": review},
        )


def literature_review_home(request):
    context = {
        "literature_reviews": LiteratureReview.objects.filter(members=request.user)
    }

    return render(
        request=request, template_name="literature_review/home.html", context=context
    )


def review_details(request, review_id):
    if not request.user.is_authenticated:
        return redirect("home")

    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user in review.members.all():
        return render(request, "literature_review/view_review.html", {"review": review})
    else:
        return redirect("home")


def make_decision(exclusions, inclusions):
    if "yes" in exclusions:
        return False
    if "no" in inclusions:
        return False

    return True


def screen_papers(request, review_id, paper_id=None):
    if not request.user.is_authenticated:
        return redirect("home")

    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        return redirect("home")

    if request.method == "GET":
        if paper_id:
            edited_index = [
                index_i
                for index_i, x in enumerate(review.papers)
                if str(x["id"]) == str(paper_id)
            ][0]
            return render(
                request,
                "literature_review/screen_paper.html",
                {
                    "review": review,
                    "paper": review.papers[edited_index],
                    "start_time": time.time(),
                },
            )

        for paper in review.papers:
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
        prior_knowledge = request.POST["prior_knowledge"]

        edited_index = [
            index_i
            for index_i, x in enumerate(review.papers)
            if str(x["id"]) == str(paper_id)
        ][
            0
        ]  # FIXME: this will fail if duplicates in DB
        review.papers[edited_index]["decisions"] = [
            {
                "reviewer_id": request.user.pk,
                "decision": decision,
                "eligibility_decision": eligibility_decision,
                "reason": reason,
                "inclusions": inclusions,
                "exclusions": exclusions,
                "stage": "title_abstract",
                "domain_relevance": int(domain_relevance),
                "topic_relevance": int(topic_relevance),
                "prior_knowledge": int(prior_knowledge),
                "screening_time": screening_time,
            }
        ]
        review.papers[edited_index]["decision"] = decision
        if len(review.papers[edited_index]["decisions"]) >= MIN_DECISIONS:
            review.papers[edited_index]["screened"] = True
        review.save()

        for paper in review.papers:
            if (
                not paper.get("decisions")
                or len(paper.get("decisions")) < MIN_DECISIONS
            ):
                return render(
                    request,
                    "literature_review/screen_paper.html",
                    {"review": review, "paper": paper},
                )


def export_review(request, review_id):
    if not request.user.is_authenticated:
        return redirect("home")

    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user in review.members.all():
        data = {
            "title": review.title,
            "description": review.description,
            "search_queries": review.search_queries,
            "inclusion_criteria": review.inclusion_criteria,
            "exclusion_criteria": review.exclusion_criteria,
            "papers": review.papers,
        }
        return HttpResponse(json.dumps(data, indent=2), content_type="application/json")


def add_seed_studies(request, review_id):
    if not request.user.is_authenticated:
        return redirect("home")

    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        return redirect("home")

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
                print(doc.header.title)
                new_papers = list(review.papers)
                new_papers.append(
                    {
                        "id": doc.pdf_md5,
                        "pdf": seed_studies_url,
                        "url": doc.header.url,
                        "title": doc.header.title,
                        "abstract": doc.abstract,
                        "snippet": doc.abstract[:300],
                        "authors": ", ".join([a.full_name for a in doc.header.authors]),
                        "venue": doc.header.journal,
                        "publication_date": doc.header.date,
                        "references": len(
                            doc.citations
                        ),  # TODO: change to n_references
                        "citations": None,
                        "core_id": None,
                        "semantic_scholar_id": None,
                        "query": None,
                        "search_engine": "Seed Study",
                        "decision": None,
                        "seed_study": True,
                    }
                )
                review.papers = new_papers
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


def automatic_screening(request, review_id):
    review = get_object_or_404(LiteratureReview, pk=review_id)
    if request.user not in review.members.all():
        return redirect("home")

    import inspect
    from document_classification.registry import MLRegistry
    from document_classification.classifiers.dummy import DummyClassifier

    if request.method == "GET":
        try:
            registry = MLRegistry()  # create ML registry
            # add to ML registry
            registry.add_algorithm(endpoint_name=review.id,
                                   algorithm_object=DummyClassifier(),
                                   algorithm_name="dummy classifier",
                                   algorithm_status="production",
                                   algorithm_version="0.0.1",
                                   owner=request.user,
                                   algorithm_description="Dummy classifier always predicting '1'.",
                                   algorithm_code=inspect.getsource(DummyClassifier))
        except Exception as e:
            print("Exception while loading the algorithms to the registry,", e)

        return render(
            request=request,
            template_name="literature_review/view_review.html",
            context={"review": review},
        )