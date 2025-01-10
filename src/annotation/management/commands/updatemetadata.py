"""Defines the command to update metadata columns."""
from annotation.models import Annotation
from annotation.models import Entry
from annotation.models import extract_title_word
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Update the metadata columns."""

    def handle(self, *args, **options):
        """Update the metadata in the database."""
        self.__update_entry_metadata()
        self.__update_annotation_metadata()

    def __update_entry_metadata(self):
        """Update the metadata of the `Entry` model."""
        for entry in Entry.objects.all():
            entry.text_length = len(entry.text)
            entry.title_word = extract_title_word(entry.text)
            entry.save()

    def __update_annotation_metadata(self):
        """Update the metadata for the `Annotation` model."""
        for annotation in Annotation.objects.all():
            annotation.text_length = len(annotation.text)
            annotation.title_word = extract_title_word(annotation.text)
            annotation.save()
