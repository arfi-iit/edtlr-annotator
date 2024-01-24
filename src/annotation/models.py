"""Contains the models."""
from django.db import models


# Create your models here.
class OcrResult(models.Model):
    """Represents a pair of (page image, OCR text)."""

    page_no = models.IntegerField(primary_key=True)
    image_path = models.CharField(unique=True, null=False, max_length=1024)
    text = models.CharField(max_length=4096, null=False)
