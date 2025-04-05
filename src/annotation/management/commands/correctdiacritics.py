"""Defines the command for replacing diacritics with cedilla to diacritics with comma below."""
from django.core.management.base import BaseCommand
from annotation.models import Entry
from annotation.models import Annotation
from annotation.utils.xml2edtlrmd import correct_diacritics


class Command(BaseCommand):
    """Implements the command for correcting diacritics."""

    help = "Corrects diacritics in entries, and annotations."

    def add_arguments(self, parser):
        """Add command-line arguments.

        Parameters
        ----------
        parser: argparse.Parser, required
            The arguments parser.
        """
        parser.add_argument('--batch-size',
                            type=int,
                            default=1000,
                            help="Number of records to process in each batch")

    def handle(self, *args, **kwargs):
        """Corrects the diacritics."""
        batch_size = kwargs['batch_size'] if 'batch_size' in kwargs else 1000

        self.__correct_entries(batch_size)
        self.__correct_annotations(batch_size)

    def __correct_entries(self, batch_size: int):
        """Corrects the diacritics in annotations.

        Parameters
        ----------
        batch_size: int, required
            The batch size.
        """
        num_updated = 0
        num_entries = Entry.objects.count()
        for start in range(0, num_entries, batch_size):
            entries = Entry.objects.all()[start:start + batch_size]
            for entry in entries:
                corrected_text = correct_diacritics(entry.text)
                if corrected_text != entry.text:
                    entry.set_text(corrected_text)
                    num_updated += 1
                    entry.save()
            if num_updated > 0:
                message = f'Corrected diacritics in {num_updated} entries.'
                self.stdout.write(self.style.SUCCESS(message))
        self.stdout.write(
            self.style.SUCCESS("Finished correcting diacritics in entries."))

    def __correct_annotations(self, batch_size: int):
        """Corrects the diacritics in annotations.

        Parameters
        ----------
        batch_size: int, required
            The batch size.
        """
        num_updated = 0
        num_annotations = Annotation.objects.count()
        for start in range(0, num_annotations, batch_size):
            annotations = Annotation.objects.all()[start:start + batch_size]
            for annotation in annotations:
                corrected_text = correct_diacritics(annotation.text)
                if corrected_text != annotation.text:
                    annotation.set_text(corrected_text)
                    num_updated += 1
                    annotation.save()
            if num_updated > 0:
                message = f'Corrected diacritics in {num_updated} annotations.'
                self.stdout.write(self.style.SUCCESS(message))
        self.stdout.write(
            self.style.SUCCESS(
                "Finished correcting diacritics in annotations."))
