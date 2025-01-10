"""Defines the Volume model."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Volume(models.Model):
    """Represents a volume of the dictionary."""

    class Meta:
        """Defines the metadata of the Volume model."""

        verbose_name = _('volume')
        verbose_name_plural = _('volumes')

    id = models.AutoField(verbose_name="id", primary_key=True)
    name = models.CharField(unique=True,
                            null=False,
                            max_length=128,
                            verbose_name=_('name'))

    def __str__(self):
        """Override the string representation of the model."""
        return str(self.name)
