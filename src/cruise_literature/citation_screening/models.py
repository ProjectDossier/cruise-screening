from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from cruise_literature import settings

REVIEW_TITLE_MAX_LEN = 100
REVIEW_TITLE_MIN_LEN = 3


class CitationScreening(models.Model):
    inclusion_criteria = models.TextField(
        _("inclusion criteria"),
        blank=True,
        null=True,
        default="",
        help_text="Inclusion Criteria",
    )
    exclusion_criteria = models.TextField(
        _("exclusion criteria"),
        blank=True,
        null=True,
        default="",
        help_text="Exclusion Criteria",
    )


#     function assign() which will create assignments of papers for people


class LiteratureReview(models.Model):
    title = models.CharField(
        _("title"),
        blank=True,
        null=True,
        default="",
        max_length=REVIEW_TITLE_MAX_LEN,
        help_text=f"Literature review name must be between {REVIEW_TITLE_MIN_LEN} and {REVIEW_TITLE_MAX_LEN} long.",
        validators=[
            MinLengthValidator(REVIEW_TITLE_MIN_LEN),
            MaxLengthValidator(REVIEW_TITLE_MAX_LEN),
        ],
    )
    description = models.TextField(
        _("description"),
        blank=True,
        null=True,
        default="",
        help_text="Project description",
    )
    first_screening = models.ForeignKey(
        CitationScreening,
        on_delete=models.CASCADE,
        related_name="title_abstract_screening",
        help_text="Citation screening ID",
    )


class LiteratureReviewMember(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
        help_text="User ID",
    )
    literature_review = models.ForeignKey(
        LiteratureReview, on_delete=models.CASCADE, help_text="Literature Review ID"
    )
