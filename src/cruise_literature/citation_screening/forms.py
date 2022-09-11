from dataclasses import asdict
import datetime

from django import forms

from .models import LiteratureReview, LiteratureReviewMember
from django.contrib.postgres.forms import SimpleArrayField
from document_search.search_semantic_scholar import search_semantic_scholar
from document_search.search_core import search_core


class NewLiteratureReviewForm(forms.ModelForm):
    title = forms.CharField()
    search_queries = SimpleArrayField(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(),
        help_text="Type in your search queries, every query in a new line",
    )
    inclusion_criteria = SimpleArrayField(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(),
        help_text="Type in your inclusion criteria, every one in a new line",
    )
    exclusion_criteria = SimpleArrayField(
        forms.CharField(),
        delimiter="\n",
        widget=forms.Textarea(),
        help_text="Type in your exclusion criteria, every one in a new line",
    )
    top_k = forms.IntegerField(
        initial=10,
        max_value=200,
        min_value=10,
        help_text="How many records do you want to retrieve?",
    )
    project_deadline = forms.DateField(initial=datetime.date.today,
                                       widget=forms.SelectDateWidget(years=range(2020, 2030)))

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
            search_engines = {"semantic_scholar": search_semantic_scholar, "CORE": search_core}
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
