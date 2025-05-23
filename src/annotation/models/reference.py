"""Defines the Reference model."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Reference(models.Model):
    """Represents a reference."""

    class Meta:
        """Defines the metadata of the Reference model."""

        verbose_name = _('reference')
        verbose_name_plural = _('references')

    id = models.AutoField(verbose_name="id", primary_key=True)
    text = models.TextField(verbose_name="text",
                            null=False,
                            unique=True,
                            max_length=250)
    is_approved = models.BooleanField(verbose_name=_("is_approved"),
                                      blank=False,
                                      null=False)
    row_creation_timestamp = models.DateTimeField(
        verbose_name=_('row creation timestamp'),
        blank=False,
        null=False,
        default=timezone.now)

    row_update_timestamp = models.DateTimeField(
        verbose_name=_('row update timestamp'),
        blank=False,
        null=True,
        auto_now=True)

    def __str__(self):
        """Override the string representation of the model."""
        return self.text
