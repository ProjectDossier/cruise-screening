import copy
from typing import Tuple, List

from django.contrib.postgres.fields import ArrayField
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from cruise_literature import settings
from organisations.models import Organisation
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

    REVIEW_TYPES = [
        ("RE", "Literature Review"),
        ("AN", "Annotation Task"),
    ]
    review_type = models.CharField(
        max_length=2,
        choices=REVIEW_TYPES,
        default='AN',
    )

    @property
    def obligatory_fields(self):
        if self.review_type == 'AN':
            return ['inclusion', 'exclusion', 'relevance', 'decision', 'past_knowledge']
        elif self.review_type == 'RE':
            return ['decision']
        else:
            raise ValueError(f'Unknown review type: {self.review_type}')

    project_deadline = models.DateField()
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="organisation",
    )

    annotations_per_paper = models.IntegerField(
        default=1,
        help_text="How many reviewers need to screen every paper. Default is 1.",
        validators=[MinValueValidator(1), MaxValueValidator(3)],
    )

    search_queries = ArrayField(models.CharField(max_length=250, blank=True), null=True)

    criteria = models.JSONField(null=True, blank=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="LiteratureReviewMember",
        through_fields=("literature_review", "member"),
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    data_format_version = models.IntegerField(
        default=3,
        help_text="Version of the data format. This is used to migrate data between versions.",
    )

    ready_for_screening = models.BooleanField(
        default=False,
        help_text="If True, than papers were distributed between reviewers for manual screening.",
    )
    search_updated_at = models.DateTimeField(
        null=True, blank=True, help_text="When the search was last updated."
    )
    papers_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the papers were last updated. Includes updating by search or documents upload.",
    )

    papers = models.JSONField(
        null=True, help_text="All papers in the literature review."
    )

    def __init__(self, *args, **kwargs):
        super(LiteratureReview, self).__init__(*args, **kwargs)
        self.old_papers = copy.copy(self.papers)

    def save(self, *args, **kwargs):
        # check if papers are changed and update papers_updated_at
        if self.papers and self.papers != self.old_papers:
            self.papers_updated_at = timezone.now()
        super(LiteratureReview, self).save(*args, **kwargs)

    @property
    def number_of_papers(self):
        if self.data_format_version < 3:
            return len(self.papers) if self.papers else 0
        else:
            return len(self.papers.values()) if self.papers else 0

    @property
    def number_of_pdfs(self):
        if self.data_format_version < 3:
            return (
                sum(bool(paper["pdf"]) for paper in self.papers) if self.papers else 0
            )
        else:
            return (
                sum(bool(paper["pdf"]) for paper in self.papers.values())
                if self.papers
                else 0
            )

    @property
    def number_of_screened(self):
        if self.papers:
            if self.data_format_version < 3:
                return sum(bool(paper.get("screened")) for paper in self.papers)
            else:
                return sum(
                    bool(paper.get("screened")) for paper in self.papers.values()
                )
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
        if self.data_format_version < 3:
            _papers = self.papers
        else:
            _papers = self.papers.values()
        for paper in _papers:
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

    @property
    def automatic_decisions_count(self) -> Tuple[int, int, int, int]:
        """returns include, not sure, exclude, no decision"""
        if not self.papers:
            return 0, 0, 0, 0
        includes = 0
        not_sures = 0
        excludes = 0
        no_decision = 0
        if self.data_format_version < 3:
            _papers = self.papers
        else:
            _papers = self.papers.values()

        for paper in _papers:
            if paper.get("automatic_decisions"):
                _decisions = [
                    decision["decision"] for decision in paper["automatic_decisions"]
                ]
                decision = convert_decisions(resolve_decisions(_decisions))
                if decision == "1":
                    includes += 1
                elif decision == "-1":
                    not_sures += 1
                elif decision == "0":
                    excludes += 1
            else:
                no_decision += 1
        return includes, not_sures, excludes, no_decision

    @property
    def can_screen_automatically(self) -> bool:
        """This is used to determine if the literature review can be screened automatically.
        Automatic screening requires at least 8 manual annotations out of which at least 3 are includes and not sures
        and additional three are excludes.

        :return: Returns True if the literature review has enough annotations.
        """
        if self.number_of_screened < 8:
            return False
        includes, not_sures, excludes, _ = self.decisions_count
        return (includes + not_sures) >= 3 and excludes >= 3


class LiteratureReviewMember(models.Model):
    """A user can be a member of a literature review."""

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lrm_through",
        help_text="User ID",
    )
    literature_review = models.ForeignKey(
        LiteratureReview, on_delete=models.CASCADE, help_text="Literature Review ID"
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lrm_added_by",
        help_text="User ID",
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


def convert_decisions(text: str) -> str:
    if text == "yes":
        return "1"
    elif text == "no":
        return "0"
    elif text == "maybe":
        return "-1"
    else:
        return "-1"


def resolve_decisions(_decisions: List[str]):
    if len(_decisions) == 1:
        return _decisions[0]
    else:
        return max(set(_decisions), key=_decisions.count)
