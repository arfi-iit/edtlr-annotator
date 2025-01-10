"""Defines the Page model."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from .volume import Volume


class Page(models.Model):
    """Represents a pair of (page image, OCR text)."""

    id = models.AutoField(verbose_name="id", primary_key=True)
    volume = models.ForeignKey(Volume,
                               on_delete=models.CASCADE,
                               default=1,
                               verbose_name=_('volume'))
    page_no = models.PositiveIntegerField(null=False,
                                          verbose_name=_('page number'))
    image_path = models.CharField(unique=True,
                                  null=False,
                                  max_length=1024,
                                  verbose_name=_('image path'))

    def __str__(self):
        """Override the string representation of the model."""
        return str(self.page_no)

    class Meta:
        """Defines the metadata of the Page model."""

        verbose_name = _('page')
        verbose_name_plural = _('pages')
        constraints = [
            models.UniqueConstraint(fields=["volume", "page_no"],
                                    name="UX_volume_id_page_no")
        ]
