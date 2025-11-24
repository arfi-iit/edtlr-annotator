"""Defines the view settings."""
from django.conf import settings
from enum import Enum

MAX_CONCURRENT_ANNOTATORS = int(
    getattr(settings, "MAX_CONCURRENT_ANNOTATORS", 2))


class ApplicationModes(Enum):
    """Defines the modes in which the application runs."""

    AnnotateEntries = 0
    WriteEntries = 1


match getattr(settings, 'APPLICATION_MODE', 'annotate'):
    case 'annotate':
        APPLICATION_MODE = ApplicationModes.AnnotateEntries
    case _:
        APPLICATION_MODE = ApplicationModes.WriteEntries
