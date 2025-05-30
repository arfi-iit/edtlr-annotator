"""Defines the EvaluationInterval model."""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class EvaluationInterval(models.Model):
    """Represents a time interval used to evaluate annotators."""

    class Meta:
        """Defines the metadata of the EvaluationInterval model."""

        verbose_name = _('evaluation interval')
        verbose_name_plural = _('evaluation intervals')

    id = models.AutoField(verbose_name="id", primary_key=True)
    name = models.CharField(unique=True,
                            null=False,
                            max_length=128,
                            verbose_name=_('name'))
    start_date = models.DateField(verbose_name=_('start date'),
                                  blank=False,
                                  null=False)
    end_date = models.DateField(verbose_name=_('end date'),
                                blank=False,
                                null=False)
