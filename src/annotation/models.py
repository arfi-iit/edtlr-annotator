"""Contains the models."""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Volume(models.Model):
    """Represents a volume of the dictionary."""

    id = models.AutoField(verbose_name="id", primary_key=True)
    name = models.CharField(unique=True, null=False, max_length=128)


class Page(models.Model):
    """Represents a pair of (page image, OCR text)."""

    id = models.AutoField(verbose_name="id", primary_key=True)
    volume_id = models.ForeignKey(Volume,
                                  on_delete=models.CASCADE,
                                  verbose_name="volume_id")
    page_no = models.PositiveIntegerField(verbose_name="page_no",
                                          unique=True,
                                          null=False)
    image_path = models.CharField(unique=True, null=False, max_length=1024)
    text = models.TextField(max_length=8192, null=False)

    class Meta:
        """Metadata of the Page model."""
        constraints = [
            models.UniqueConstraint(fields=["volume_id", "page_no"],
                                    name="UX_volume_id_page_no")
        ]


class Annotation(models.Model):
    """Represents an annotation."""

    class AnnotationStatus(models.TextChoices):
        """Defines the possible values of an annotation status."""

        IN_PROGRESS = 'InProgress', _('In progress')
        COMPLETE = 'Complete', _('Complete')
        CONFLICT = 'Conflict', _('Conflict')

    id = models.AutoField(verbose_name="id", primary_key=True)
    page_id = models.ForeignKey(Page,
                                on_delete=models.CASCADE,
                                verbose_name="page_id")
    user_id = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                verbose_name="user_id")
    contents = models.TextField(verbose_name="contents", null=True)
    status = models.CharField(max_length=32,
                              choices=AnnotationStatus,
                              null=False,
                              default=AnnotationStatus.IN_PROGRESS)
    version = models.PositiveSmallIntegerField()
    row_creation_timestamp = models.DateTimeField(blank=False,
                                                  null=False,
                                                  default=timezone.now)
    row_update_timestamp = models.DateTimeField(auto_now=True)
