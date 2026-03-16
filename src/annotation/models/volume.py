"""Defines the Volume model."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from .dictionary import Dictionary


class Volume(models.Model):
    """Represents a volume of the dictionary."""

    class Meta:
        """Defines the metadata of the Volume model."""

        verbose_name = _('volume')
        verbose_name_plural = _('volumes')
        constraints = [
            models.UniqueConstraint(fields=['dictionary', 'name'],
                                    name='unique_volumes_per_dictionary')
        ]

    id = models.AutoField(verbose_name="id", primary_key=True)
    dictionary = models.ForeignKey(Dictionary,
                                   on_delete=models.PROTECT,
                                   verbose_name=_('dictionary'),
                                   null=False,
                                   default=1)
    name = models.CharField(null=False, max_length=128, verbose_name=_('name'))

    def __str__(self):
        """Override the string representation of the model."""
        return str(self.name)
