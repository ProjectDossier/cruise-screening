from dataclasses import asdict
from django import forms

from django.forms import ModelForm, CharField, Textarea
from .models import LiteratureReview, LiteratureReviewMember
from django.contrib.postgres.forms import SimpleArrayField
from document_search.search_semantic_scholar import search_semantic_scholar


class NewLiteratureReviewForm(ModelForm):
    search_queries = SimpleArrayField(
        CharField(),
        delimiter="\n",
        widget=Textarea(),
        help_text="Type in your search queries, every query in a new line",
    )
    inclusion_criteria = SimpleArrayField(
        CharField(),
        delimiter="\n",
        widget=Textarea(),
        help_text="Type in your inclusion criteria, every one in a new line",
    )
    exclusion_criteria = SimpleArrayField(
        CharField(),
        delimiter="\n",
        widget=Textarea(),
        help_text="Type in your exclusion criteria, every one in a new line",
    )
    top_k = forms.IntegerField(
        max_value=200,
        min_value=10,
        help_text="How many records do you want to retrieve?",
    )

    class Meta:
        model = LiteratureReview
        fields = (
            "title",
            "description",
            "search_queries",
            "inclusion_criteria",
            "exclusion_criteria",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(NewLiteratureReviewForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(NewLiteratureReviewForm, self).save(commit=False)
        top_k = self.data.get("top_k")

        queries = self.cleaned_data["search_queries"]
        results = []
        for query in queries:
            # TODO: add more search engines
            for paper in search_semantic_scholar(query=query, index="", top_k=top_k):
                paper = asdict(paper)
                paper["query"] = query
                paper["search_engine"] = "semantic_scholar"
                paper["decision"] = None
                results.append(paper)
        instance.papers = results

        if commit:
            instance.save()
            member = LiteratureReviewMember(
                member=self.user, literature_review=instance, role="AD"
            )
            member.save()

        return instance