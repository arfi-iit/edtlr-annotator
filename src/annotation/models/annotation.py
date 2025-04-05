"""Defines the Annotation model."""
from annotation.models.entry import Entry
from annotation.models.utils import extract_title_word
from annotation.models.utils import remove_diacritics
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Annotation(models.Model):
    """Represents an annotation."""

    class AnnotationStatus(models.TextChoices):
        """Defines the possible values of an annotation status."""

        IN_PROGRESS = 'InProgress', _('In progress')
        COMPLETE = 'Complete', _('Complete')
        CONFLICT = 'Conflict', _('Conflict')

    class Meta:
        """Defines the metadata of the Annotation model."""

        verbose_name = _('annotation')
        verbose_name_plural = _('annotations')

    id = models.AutoField(verbose_name="id", primary_key=True)
    entry = models.ForeignKey(Entry,
                              on_delete=models.CASCADE,
                              null=False,
                              default=1,
                              verbose_name=_('entry'))
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             default=1,
                             verbose_name=_('user'))
    text = models.TextField(verbose_name="text", null=True, max_length=250_000)
    title_word = models.TextField(max_length=100,
                                  null=False,
                                  default='',
                                  verbose_name=_('title word'))
    title_word_normalized = models.TextField(max_length=100,
                                             null=False,
                                             default='')
    text_length = models.IntegerField(null=False,
                                      default=0,
                                      verbose_name=_('text length'))
    status = models.CharField(max_length=32,
                              choices=AnnotationStatus,
                              null=False,
                              default=AnnotationStatus.IN_PROGRESS)
    version = models.PositiveSmallIntegerField(verbose_name=_('version'))
    row_creation_timestamp = models.DateTimeField(
        blank=False,
        null=False,
        default=timezone.now,
        verbose_name=_('row creation timestamp'))
    row_update_timestamp = models.DateTimeField(
        null=True, verbose_name=_('row update timestamp'))

    def set_text(self, text: str):
        """Set the  text of the annotation to the specified value and update metadata.

        Parameters
        ----------
        text: str, required
            The text of the annotation.
        """
        self.text = text
        self.text_length = len(text)
        self.title_word = extract_title_word(text)
        self.title_word_normalized = remove_diacritics(self.title_word)
        self.version = self.version + 1 if self.version is not None else 1

    def __str__(self):
        """Override the string representation of the model."""
        return self.title_word
