from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

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
        null=True,
        related_name="title_abstract_screening",
        help_text="Citation screening ID",
    )

    # TODO: next steps - add search queries and inclusion criteria as json fields to the form
    # so they have to be textfield (ideally) or charfield, and assumption that every item is a new line
    # after creating, we will run queries to the search engine and load all search results to the review into papers

    search_queries = ArrayField(models.CharField(max_length=250, blank=True), null=True)
    inclusion_criteria = ArrayField(models.CharField(max_length=250, blank=True), null=True)
    exclusion_criteria = ArrayField(models.CharField(max_length=250, blank=True), null=True)

    papers = models.JSONField(null=True)
    # { [{
    #     "id": 1,
    #     article: Article,
    #     query: 'sdasdasd asd asda',
    #     search_engine: ['core'],
    #     decisions: [
    #         {
    #             "reviewer_id": 11,
    #             "decision": {0|1|-1},
    #             "reason": [E1, E2, E3],
    #             "stage": first,
    #             "relevance": [1,2,1,1],
    #          },
    #         ...
    #     ]
    #     },
    #     ...
    # ]}


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
