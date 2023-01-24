import datetime
import hashlib
import json
from typing import Dict, List

import bibtexparser
import rispy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from requests import HTTPError

from .forms import NewLiteratureReviewForm, EditLiteratureReviewForm
from .models import LiteratureReview
from utils.process_pdf import parse_doc_grobid
from utils.django_tags import first_n_words


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
        paper = {
            "title": entry.get("title"),
            "abstract": entry.get("abstract"),
            "authors": ", ".join(entry.get("authors")),
            "venue": entry.get("journal_name"),
            "publication_date": entry.get("year"),
            "doi": entry.get("doi"),
            "url": entry.get("url"),
            "n_references": None,
            "n_citations": None,
            "decisions": [],
            "decision": None,
            "screened": False,
            "included": False,
        }
        if paper["url"] is None:
            paper["url"] = f"https://www.doi.org/{paper['doi']}"
        paper["keywords"] = entry.get("keywords")
        paper["pdf"] = entry.get("pdf")
        paper["id"] = entry.get("id")

        if paper["id"] is None:
            paper["id"] = hashlib.md5(paper["title"].encode("utf-8")).hexdigest()
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
