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
    )
    discipline = forms.ModelChoiceField(
        queryset=KnowledgeArea.objects.all(),
        widget=forms.Select(attrs={"class": "select"}),
    )
    annotations_per_paper = forms.ChoiceField(
        choices=[(1, 1), (2, 2), (3, 3)], widget=forms.Select(attrs={"class": "select"})
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
        instance = super(NewLiteratureReviewForm, self).save(commit=False)
        top_k = self.data.get("top_k")

        queries = self.cleaned_data["search_queries"]
        results = {}
        for query in queries:
            # TODO: add more search engines
            search_engines = {
                "semantic_scholar": search_semantic_scholar,
                "CORE": search_core,
            }
            for search_engine_name, search_method in search_engines.items():
                for paper in search_method(query=query, index="", top_k=top_k):
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
