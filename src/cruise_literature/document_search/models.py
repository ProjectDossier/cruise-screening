from django.db import models

from django.utils.translation import gettext_lazy as _


class SearchEngine(models.Model):
    """Search engine that can be used to search for documents."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField()

    search_method = models.CharField(max_length=255, blank=True, null=True)

    is_available_for_search = models.BooleanField(
        default=True, verbose_name=_("Is available for search")
    )
    is_available_for_review = models.BooleanField(
        default=True, verbose_name=_("Available for literature review")
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return self.name
