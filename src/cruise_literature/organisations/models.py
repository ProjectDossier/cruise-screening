import logging

from django.conf import settings
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class Organisation(models.Model):
    """Model class representing an organisation."""

    title = models.CharField(_("organisation title"), max_length=1000, null=False)
    description = models.TextField(_("organisation description"), null=True, blank=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="organisations",
        through="OrganisationMember",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="organisation",
        verbose_name=_("created_by"),
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def add_user(self, user):
        if self.members.filter(pk=user.pk).exists():
            logger.debug("User already exists in organisation.")
            return

        with transaction.atomic():
            om = OrganisationMember(user=user, organisation=self)
            om.save()

            return om

    def remove_user(self, user):
        if not self.members.filter(pk=user.pk).exists():
            logger.debug("User does not exist in organisation.")
            return

        with transaction.atomic():
            om = OrganisationMember.objects.get(user=user, organisation=self)
            om.delete()

            return om

    @property
    def number_of_members(self):
        """Return the number of members in the organisation."""
        return self.members.count()


class OrganisationMember(models.Model):
    """A member of an organisation."""

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="om_through",
        help_text="User ID",
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        help_text="Organisation ID",
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    roles_choices = [
        ("AD", "Admin"),
        ("ME", "Member"),
        ("GU", "Guest"),
    ]
    role = models.CharField(
        max_length=2,
        choices=roles_choices,
        default="ME",
    )

    @classmethod
    def find_by_user(cls, user_or_user_pk, organisation_pk):
        from users.models import User

        user_pk = (
            user_or_user_pk.pk if isinstance(user_or_user_pk, User) else user_or_user_pk
        )
        return OrganisationMember.objects.get(
            user=user_pk, organisation=organisation_pk
        )

    class Meta:
        ordering = ["pk"]
