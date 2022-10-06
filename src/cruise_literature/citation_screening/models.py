from typing import Tuple

from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from cruise_literature import settings
from users.models import KnowledgeArea

REVIEW_TITLE_MAX_LEN = 100
REVIEW_TITLE_MIN_LEN = 3


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
    additional_description = models.TextField(
        blank=True,
        null=True,
        default="",
        help_text="Additional description field, for instance for topic narrative.",
    )
    discipline = models.ForeignKey(
        KnowledgeArea, on_delete=models.SET_NULL, null=True, blank=True
    )
    tags = ArrayField(
        models.CharField(max_length=250, blank=True), null=True, blank=True
    )
    search_databases = models.CharField(max_length=250, blank=True, null=True)

    creation_date = models.DateField(auto_now_add=True)
    last_edit_date = models.DateField(auto_now=True)
    project_deadline = models.DateField()

    annotations_per_paper = models.IntegerField(
        default=1,
        help_text="How many reviewers need to screen every paper. Default is 1.",
        validators=[MinValueValidator(1), MaxValueValidator(3)],
    )

    search_queries = ArrayField(models.CharField(max_length=250, blank=True), null=True)
    inclusion_criteria = ArrayField(
        models.CharField(max_length=250, blank=True), null=True
    )
    exclusion_criteria = ArrayField(
        models.CharField(max_length=250, blank=True), null=True
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="LiteratureReviewMember",
        through_fields=("literature_review", "member"),
    )

    papers = models.JSONField(null=True)

    @property
    def number_of_papers(self):
        return len(self.papers) if self.papers else 0

    @property
    def number_of_pdfs(self):
        return sum(bool(paper["pdf"]) for paper in self.papers) if self.papers else 0

    @property
    def number_of_screened(self):
        if self.papers:
            return sum(bool(paper.get("screened")) for paper in self.papers)
        else:
            return 0

    @property
    def percentage_screened(self):
        if self.number_of_papers > 0:
            return round(100 * self.number_of_screened / self.number_of_papers, 2)
        else:
            return 0.0

    @property
    def decisions_count(self) -> Tuple[int, int, int, int]:
        """returns include, not sure, exclude, no decision"""
        if not self.papers:
            return 0, 0, 0, 0
        includes = 0
        not_sures = 0
        excludes = 0
        no_decision = 0
        for paper in self.papers:
            if paper.get("decision"):
                if paper["decision"] == "1":
                    includes += 1
                elif paper["decision"] == "-1":
                    not_sures += 1
                elif paper["decision"] == "0":
                    excludes += 1
            else:
                no_decision += 1
        return includes, not_sures, excludes, no_decision


class LiteratureReviewMember(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="User ID",
    )
    literature_review = models.ForeignKey(
        LiteratureReview, on_delete=models.CASCADE, help_text="Literature Review ID"
    )

    roles_choices = [
        ("AD", "Admin"),
        ("ME", "Member"),
    ]
    role = models.CharField(
        max_length=2,
        choices=roles_choices,
        default="ME",
    )
