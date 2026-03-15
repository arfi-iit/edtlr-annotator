"""Defines the Dictionary model."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Dictionary(models.Model):
    """Represents a dictionary."""

    class Meta:
        """Defines the metadata of the Dictionary model."""

        verbose_name = _('dictionary')
        verbose_name_plural = _('dictionaries')

    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(unique=True,
                            null=False,
                            max_length=256,
                            verbose_name=_('name'))
    is_active = models.BooleanField(verbose_name=_('is_active'),
                                    blank=False,
                                    null=False,
                                    default=True)

    def __str__(self, ):
        """Override the string representation of the model."""
        return str(self.name)
