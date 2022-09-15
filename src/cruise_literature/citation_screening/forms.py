from dataclasses import asdict
import datetime

from django import forms

from .models import LiteratureReview, LiteratureReviewMember
from django.contrib.postgres.forms import (
    SimpleArrayField,
    ValidationError,
    prefix_validation_error,
)
from document_search.search_semantic_scholar import search_semantic_scholar
from document_search.search_core import search_core
from document_search.search_google_scholar import search_google_scholar
from document_search.search_documents import search
from users.models import KnowledgeArea

SEARCH_ENGINES_DICT = {
    "SemanticScholar": search_semantic_scholar,
    "CORE": search_core,
    "CRUISE": search,
    "Google Scholar": search_google_scholar,
}


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


class NewLiteratureReviewForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input form_required"})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"})
    )
    search_queries = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"}),
        label="Type in your search queries, every query in a new line",
    )
    inclusion_criteria = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"}),
        label="Type in your inclusion criteria, every one in a new line",
    )
    exclusion_criteria = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"}),
        label="Type in your exclusion criteria, every one in a new line",
    )
    project_deadline = forms.DateField(
        initial=datetime.date.today,
        widget=forms.SelectDateWidget(years=range(2020, 2030)),
    )
    tags = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter=",",
        widget=forms.TextInput(attrs={"class": "input"}),
        label="Add optional tags, coma separated",
        required=False,
    )
    discipline = forms.ModelChoiceField(
        queryset=KnowledgeArea.objects.all(),
        widget=forms.Select(attrs={"class": "select"}),
        required=False,
    )
    annotations_per_paper = forms.ChoiceField(
        choices=[(1, 1), (2, 2), (3, 3)], widget=forms.Select(attrs={"class": "select"})
    )
    search_engines = forms.MultipleChoiceField(
        label="Select search engines where you want to search for papers. By default it searches in first three.",
        choices=[(k, ' '.join(k.split('_'))) for k in SEARCH_ENGINES_DICT.keys()],
        initial=list(SEARCH_ENGINES_DICT.keys())[:3],  # only first three search engines by default
        widget=forms.SelectMultiple(attrs={"class": "select is-multiple is-medium"}),
        help_text="Selecting Google Scholar will drastically increase the search time."
    )
    top_k = forms.IntegerField(
        initial=25,
        max_value=200,
        min_value=10,
        label="How many records do you want to retrieve?",
        widget=forms.NumberInput(attrs={"class": "input"})
    )

    class Meta:
        model = LiteratureReview
        fields = (
            "title",
            "description",
            "search_queries",
            "inclusion_criteria",
            "exclusion_criteria",
            "project_deadline",
            "tags",
            "discipline",
            "annotations_per_paper",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(NewLiteratureReviewForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        INDEX_NAME = 'papers'  # TODO: get rid of this parameter
        instance = super(NewLiteratureReviewForm, self).save(commit=False)
        top_k = self.cleaned_data["top_k"]
        search_engines = self.cleaned_data["search_engines"]

        queries = self.cleaned_data["search_queries"]
        results = {}
        for query in queries:
            # TODO: add more search engines
            for search_engine_name in search_engines:
                search_method = SEARCH_ENGINES_DICT[search_engine_name]
                for paper in search_method(query=query, index=INDEX_NAME, top_k=top_k):
                    paper = asdict(paper)
                    paper["query"] = query
                    paper["search_engine"] = search_engine_name
                    paper["decision"] = None
                    results[paper["id"]] = paper

        instance.papers = list(results.values())

        if commit:
            instance.save()
            member = LiteratureReviewMember(
                member=self.user, literature_review=instance, role="AD"
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
        label="Type in your inclusion criteria, every one in a new line",
    )
    exclusion_criteria = ArrayFieldStripWhitespaces(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(attrs={"class": "textarea is-small form_required"}),
        label="Type in your exclusion criteria, every one in a new line",
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
            "inclusion_criteria",
            "exclusion_criteria",
            "tags",
        )