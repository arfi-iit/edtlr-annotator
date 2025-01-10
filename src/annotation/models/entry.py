"""Defines the Entry model."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from .utils import extract_entry


class Entry(models.Model):
    """Represents a dictionary entry."""

    id = models.AutoField(verbose_name="id", primary_key=True)
    text = models.TextField(max_length=250_000, null=False)

    title_word = models.TextField(max_length=100,
                                  null=False,
                                  default='',
                                  verbose_name=_('title word'))
    text_length = models.IntegerField(null=False,
                                      default=0,
                                      verbose_name=_('text length'))

    class Meta:
        """Defines metadata of the Entry model."""

        verbose_name = _('entry')
        verbose_name_plural = _('entries')

    def set_text(self, text: str):
        """Set the  text of the entry to the specified value and update metadata.

        Parameters
        ----------
        text: str, required
            The text of the enty.
        """
        self.text = text
        self.text_length = len(text)
        self.title_word = extract_entry(text)

    def __str__(self):
        """Override the string representation of the model."""
        return self.title_word
