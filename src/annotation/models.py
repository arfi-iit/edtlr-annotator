"""Contains the models."""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Page(models.Model):
    """Represents a pair of (page image, OCR text)."""

    id = models.AutoField(verbose_name="id", primary_key=True)
    image_path = models.CharField(unique=True, null=False, max_length=1024)
    text = models.TextField(max_length=8192, null=False)


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
    content = models.JSONField(verbose_name="content")
    status = models.CharField(max_length=32,
                              choices=AnnotationStatus,
                              null=False,
                              default=AnnotationStatus.IN_PROGRESS)
    version = models.PositiveSmallIntegerField()
    row_creation_timestamp = models.DateTimeField(blank=False,
                                                  null=False,
                                                  default=timezone.now)
    row_update_timestamp = models.DateTimeField(auto_now=True)
