from django.forms import ModelForm
from .models import LiteratureReview


class NewLiteratureReviewForm(ModelForm):
    class Meta:
        model = LiteratureReview
        fields = (
            "title",
            "description",
        )
