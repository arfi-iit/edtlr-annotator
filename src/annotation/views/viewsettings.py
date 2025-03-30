"""Defines the view settings."""
from django.conf import settings

MAX_CONCURRENT_ANNOTATORS = int(
    getattr(settings, "MAX_CONCURRENT_ANNOTATORS", 2))
