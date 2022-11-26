from django.db import models

from django.utils.translation import gettext_lazy as _


class SearchEngine(models.Model):
    """Search engine that can be used to search for documents."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField()

    search_method = models.CharField(max_length=255, blank=True, null=True)

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return self.name


