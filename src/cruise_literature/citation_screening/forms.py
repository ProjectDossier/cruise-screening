from dataclasses import asdict
from django import forms

from django.forms import ModelForm, CharField, Textarea
from .models import LiteratureReview, LiteratureReviewMember
from django.contrib.postgres.forms import SimpleArrayField
from document_search.search_semantic_scholar import search_semantic_scholar


class NewLiteratureReviewForm(ModelForm):
    search_queries = SimpleArrayField(CharField(), delimiter="\n", widget=Textarea())
    inclusion_criteria = SimpleArrayField(
        CharField(), delimiter="\n", widget=Textarea()
    )
    exclusion_criteria = SimpleArrayField(
        CharField(), delimiter="\n", widget=Textarea()
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

        queries = self.cleaned_data["search_queries"]
        results = []
        for query in queries:
            results.extend(
                [
                    asdict(x)
                    for x in search_semantic_scholar(query=query, index="", top_k=3)
                ]
            )
        instance.papers = results

        if commit:
            instance.save()
            member = LiteratureReviewMember(
                member=self.user, literature_review=instance, role="AD"
            )
            member.save()

        return instance
