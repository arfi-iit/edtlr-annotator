"""Defines the EvaluationInterval model."""
from django.db import models
from datetime import date
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

    def __str__(self):
        """Override the string representation of the model."""
        return self.name

    def contains(self, dt: date):
        """Check if the current interval contains the given date.

        Parameters
        ----------
        dt: datetime.date, required
            The date to check.

        Returns
        -------
        contains: bool
            True if the time point is greater or equal to start date, and less than end date; False otherwise.
        """
        return self.start_date <= dt and dt < self.end_date
