from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from literature_review.models import LiteratureReview, LiteratureReviewMember
from organisations.models import Organisation
from users.models import KnowledgeArea


class CitationScreening(models.Model):
    """Class representing one citation screening task: first/second level screening."""

    literature_review = models.ForeignKey(
        LiteratureReview, on_delete=models.CASCADE, help_text="Literature Review ID"
    )
    screening_level = models.IntegerField(
        default=1,
        help_text="Screening level: 1 or 2",
        choices=[(1, "Title and abstract screening"), (2, "Full-text screening")],
        validators=[MinValueValidator(1), MaxValueValidator(2)],
    )
    tasks = models.JSONField(null=True)
    tasks_updated_at = models.DateTimeField(
        null=True, blank=True, help_text="When tasks were last redistributed."
    )
    distributed_papers = models.JSONField(
        null=True,
        help_text="List of papers which were already distributed among reviewers.",
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
