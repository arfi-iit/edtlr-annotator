"""Defines the EntryPage model."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from .entry import Entry
from .page import Page


class EntryPage(models.Model):
    """Represents an association between a page and a dictionary entry."""

    id = models.AutoField(verbose_name="id", primary_key=True)
    entry = models.ForeignKey(Entry,
                              on_delete=models.CASCADE,
                              verbose_name=_('entry'))
    page = models.ForeignKey(Page,
                             on_delete=models.CASCADE,
                             verbose_name=_('page'))

    class Meta:
        """Defines the metadata of the EntryPage model."""

        verbose_name = _('page entry')
        verbose_name_plural = _('page entries')
        constraints = [
            models.UniqueConstraint(fields=["entry", "page"],
                                    name="UX_entry_id_page_id")
        ]
