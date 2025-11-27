"""Defines the view settings."""
from django.conf import settings
from enum import Enum

MAX_CONCURRENT_ANNOTATORS = int(getattr(settings, "MAX_CONCURRENT_ANNOTATORS", 2))
AUTOMATIC_REFERENCE_ANNOTATION = getattr(settings, 'AUTOMATIC_REFERENCE_ANNOTATION', False)
PRESERVE_ENTRY_TEXT = getattr(settings, 'PRESERVE_ENTRY_TEXT', True)


class ApplicationModes(Enum):
    """Defines the modes in which the application runs."""

    CorrectAnnotatedEntries = 0
    """Correct the text of the entries that have been (partially) annotated."""

    CreateEntries = 1
    """Type dictionary entries by hand."""

    AnnotateOcrText = 2
    """Annotate the raw text extracted using OCR."""


match getattr(settings, 'APPLICATION_MODE', 'annotate'):
    case 'correct':
        APPLICATION_MODE = ApplicationModes.CorrectAnnotatedEntries
    case 'annotate':
        APPLICATION_MODE = ApplicationModes.AnnotateOcrText
    case _:
        APPLICATION_MODE = ApplicationModes.CreateEntries
