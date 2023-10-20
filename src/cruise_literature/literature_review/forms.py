import copy
from dataclasses import asdict
import datetime
from typing import Dict, Any, List

from django import forms

from organisations.models import Organisation
from .models import LiteratureReview, LiteratureReviewMember
from document_search.models import SearchEngine
from django.contrib.postgres.forms import (
    SimpleArrayField,
    ValidationError,
    prefix_validation_error,
)
from document_search.search_semantic_scholar import search_semantic_scholar
from document_search.search_core import search_core
from document_search.search_google_scholar import search_google_scholar
from document_search.search_cruise import search_cruise
from document_search.search_pubmed import search_pubmed
from users.models import KnowledgeArea


class ArrayFieldStripWhitespaces(SimpleArrayField):
    """Overwrites SimpleArrayField to add a check for values provided in array.
    All empty rows are removed."""

    def to_python(self, value):
        if isinstance(value, list):
            items = value
        elif value:
            items = value.split(self.delimiter)
        else:
            items = []
        errors = []
        values = []
        for index, item in enumerate(items):
            if not item.strip():
                continue
            try:
                values.append(self.base_field.to_python(item.strip()))
            except ValidationError as error:
                errors.append(
                    prefix_validation_error(
                        error,
                        prefix=self.error_messages["item_invalid"],
                        code="item_invalid",
                        params={"nth": index},
                    )
                )
        if errors:
            raise ValidationError(errors)
        return values


def merge_papers(paper_a: Dict[str, Any], paper_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges two papers into one. If items exist in only one of the papers, they are added to the merged paper.
    If items exist in both papers, longer (for strings) or higher (for numerical) items are added to the merged paper.

    :param paper_a: first paper
    :param paper_b: second paper
    :return: merged paper
    """
    outcome_paper = copy.deepcopy(paper_a)

    keys_to_compare = [
        "abstract",
        "snippet",
        "authors",
        "url",
        "pdf",
        "venue",
        "n_citations",
        "n_references",
        "semantic_scholar_id",
        "core_id",
        "publication_date",
    ]
    for key in keys_to_compare:
        item_1 = paper_a[key]
        item_2 = paper_b[key]
        if item_1 and not item_2:
            outcome_paper[key] = item_1
        elif item_2 and not item_1:
            outcome_paper[key] = item_2
        elif item_2 and item_1:
            if isinstance(item_1, int) and isinstance(item_2, int):
                if item_1 > item_2:
                    outcome_paper[key] = item_1
                else:
                    outcome_paper[key] = item_2
            elif isinstance(item_1, str) and isinstance(item_2, str):
                if len(item_1) > len(item_2):
                    outcome_paper[key] = item_1
                else:
                    outcome_paper[key] = item_2
            else:  # todo cover rest
                outcome_paper[key] = item_1
        else:
            outcome_paper[key] = item_1

    print(f"merged {paper_a}, {paper_b}")
    outcome_paper["search_origin"] = paper_a["search_origin"] + paper_b["search_origin"]
    return outcome_paper


def deduplicate(
    results: Dict[str, Dict[str, Any]], how: str = "title"
) -> Dict[str, Dict[str, Any]]:
    """
    Deduplicates results based on the title of the paper.
    If there are multiple papers with the same title, runs merge_papers() on them.
    Currently only "title" based matching is supported.
    TODO: add more matching methods, e.g. based on DOI and other IDs.

    :param results: dictionary of results
    :param how: method for matching duplicates. 'title'
    :return: deduplicated dictionary of results
    """
    if how != "title":
        return results
    deduplicated = {}
    title_lookup = {}
    for key, paper in results.items():
        paper_title = paper["title"].lower().strip()
        if paper_title in title_lookup:
            merged_paper = merge_papers(
                paper_a=deduplicated[title_lookup[paper_title]], paper_b=paper
            )
            deduplicated.pop(title_lookup[paper_title], None)
            title_lookup.pop(paper_title, None)

            deduplicated[key] = merged_paper
            title_lookup[paper_title] = key
        else:
            deduplicated[key] = paper
            title_lookup[paper_title] = key
    return deduplicated


def create_criteria(
    inclusion_criteria: List[str],
    exclusion_criteria: List[str],
    user_id: int,
    timestamp: str,
) -> Dict[str, List[Any]]:
    """
    Creates a dictionary of criteria to be used for screening.
    :param inclusion_criteria: list of inclusion criteria
    :param exclusion_criteria: list of exclusion criteria
    :param user_id: id of the user who created the review
    :param timestamp:
    :return: dictionary of criteria
    """
    criteria = {"inclusion": [], "exclusion": []}
    for index_i, criterion in enumerate(inclusion_criteria):
        _id = f"in_{index_i}"
        if criterion:
            criteria["inclusion"].append(
                {
                    "id": _id,
                    "text": criterion,
                    "comment": "",
                    "is_active": True,
                    "added_at": timestamp,
                    "added_by": user_id,
                    "updated_at": timestamp,
                    "updated_by": user_id,
                }
            )
    for index_e, criterion in enumerate(exclusion_criteria):
        _id = f"ex_{index_e}"
        if criterion:
            criteria["exclusion"].append(
                {
                    "id": _id,
                    "text": criterion,
                    "comment": "",
                    "is_active": True,
                    "added_at": timestamp,
                    "added_by": user_id,
                    "updated_at": timestamp,
                    "updated_by": user_id,
                }
            )
    return criteria


class NewLiteratureReviewForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input form_required"}),
        label="Literature review title",
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"}),
        label="Literature review description",
    )
    search_queries = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"}),
        label="Type in your search queries, each query on a new line",
    )
    inclusion_criteria = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"}),
        label="Type in your inclusion criteria, each one on a new line",
    )
    exclusion_criteria = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"}),
        label="Type in your exclusion criteria, each one on a new line",
    )

    search_engines = forms.MultipleChoiceField(
        label=r"""Select in which search engines you want to search for the papers""",
        choices=SearchEngine.objects.filter(is_available_for_review=True).values_list(
            "id", "name"
        ),
        initial=list(
            SearchEngine.objects.filter(
                name__in=["CRUISE", "SemanticScholar", "CORE"]
            ).values_list("id", flat=True)
        ),
        widget=forms.SelectMultiple(
            attrs={
                "class": "select is-fullwidth is-multiple is-medium",
                "style": "height: 130px;",
            }
        ),
        help_text="""By default, it uses the internal CRUISE database, SemanticScholar and CORE.
        Selecting Google Scholar will drastically increase the search time.
        PubMed is the only search engine which supports Boolean operators in search queries.""",
    )
    top_k = forms.IntegerField(
        initial=25,
        max_value=500,
        min_value=10,
        label="Number of records retrieved per search query",
        widget=forms.NumberInput(attrs={"class": "input"}),
        help_text="The maximal value is 500.",
    )

    review_type = forms.ChoiceField(
        choices=LiteratureReview.REVIEW_TYPES,
        widget=forms.Select(attrs={"class": "select"}),
        help_text="""The type of the review. This fields affect the requirements during the screening process.
                  Literature review requires only filling final decision /todo/
                  Annotation task requires filling all eligibility criteria fields manually.""",
    )
    annotations_per_paper = forms.ChoiceField(
        choices=[(1, 1), (2, 2), (3, 3)],
        widget=forms.Select(attrs={"class": "select"}),
        help_text="By how many annotators each paper needs to be screened.",
    )

    project_deadline = forms.DateField(
        initial=datetime.date.today,
        widget=forms.SelectDateWidget(years=range(2020, 2030)),
    )
    discipline = forms.ModelChoiceField(
        queryset=KnowledgeArea.objects.all(),
        widget=forms.Select(attrs={"class": "select"}),
        required=False,
    )
    organisation = forms.ModelChoiceField(
        queryset=Organisation.objects.all(),
        widget=forms.Select(attrs={"class": "select"}),
        required=False,
    )
    tags = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter=",",
        widget=forms.TextInput(attrs={"class": "input"}),
        label="Add optional tags, coma separated",
        required=False,
    )

    class Meta:
        model = LiteratureReview
        fields = (
            "title",
            "description",
            "search_queries",
            "inclusion_criteria",
            "exclusion_criteria",
            "search_engines",
            "top_k",
            "review_type",
            "annotations_per_paper",
            "project_deadline",
            "discipline",
            "organisation",
            "tags",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(NewLiteratureReviewForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(NewLiteratureReviewForm, self).save(commit=False)
        top_k = self.cleaned_data["top_k"]
        search_engines = self.cleaned_data["search_engines"]

        queries = self.cleaned_data["search_queries"]
        results: Dict[str, Dict[str, Any]] = {}

        search_time_now = str(datetime.datetime.now())
        for query in queries:
            # TODO: add more search engines
            for search_engine_name in search_engines:
                search_engine = SearchEngine.objects.filter(
                    id=int(search_engine_name)
                ).first()
                search_method = eval(search_engine.search_method.split(".")[-1])

                for paper in search_method(query=query, top_k=top_k)["results"]:
                    paper = asdict(paper)

                    paper["search_origin"] = [
                        {
                            "search_engine": search_engine.name,
                            "query": query,
                            "added_at": search_time_now,
                            "added_by": self.user.username,
                            "origin": "search",
                            "id": paper["id"],
                        }
                    ]
                    paper["decision"] = None
                    paper["outcome"] = None
                    paper["screened"] = False
                    results[paper["id"]] = paper
        results = deduplicate(results=results)
        instance.papers = results
        instance.ready_for_screening = False
        instance.search_updated_at = search_time_now
        instance.papers_updated_at = search_time_now

        eligibility_criteria = create_criteria(
            self.cleaned_data["inclusion_criteria"],
            self.cleaned_data["exclusion_criteria"],
            user_id=self.user.id,
            timestamp=search_time_now,
        )
        instance.criteria = eligibility_criteria

        if commit:
            instance.save()
            member = LiteratureReviewMember(
                member=self.user,
                literature_review=instance,
                role="AD",
                added_by_id=self.user.id,
            )
            member.save()

        return instance


class EditLiteratureReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(EditLiteratureReviewForm, self).__init__(*args, **kwargs)

    title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input form_required"})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"})
    )
    inclusion_criteria = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"}),
        label="Type in your inclusion criteria, each one on a new line",
    )
    exclusion_criteria = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"}),
        label="Type in your exclusion criteria, each one on a new line",
    )
    tags = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter=",",
        widget=forms.TextInput(attrs={"class": "input"}),
        label="Add optional tags, coma separated",
        required=False,
    )
    organisation = forms.ModelChoiceField(
        queryset=Organisation.objects.all(),
        widget=forms.Select(attrs={"class": "select"}),
        required=False,
    )

    class Meta:
        model = LiteratureReview
        fields = (
            "title",
            "description",
            "inclusion_criteria",
            "exclusion_criteria",
            "tags",
            "organisation",
        )


class UpdateSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(UpdateSearchForm, self).__init__(*args, **kwargs)

    search_queries = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"}),
        label="Type in your search queries, each query one a new line",
    )
    search_engines = forms.MultipleChoiceField(
        # only SemanticScholar and PubMed
        choices=SearchEngine.objects.filter(name__in=["SemanticScholar", 'PubMed']).values_list(
            "id", "name"
        ),
        widget=forms.CheckboxSelectMultiple(),
        label="Select the search engines you want to use",
    )
