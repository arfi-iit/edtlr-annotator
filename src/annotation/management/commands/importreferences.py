"""Defines the command to import references."""
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from annotation.models.reference import Reference
from pathlib import Path


class Command(BaseCommand):
    """Imports references into the database."""

    help = "Import the references from an existing file if they don't exist already."
    requires_migrations_checks = True

    def add_arguments(self, parser):
        """Add command-line arguments.

        Parameters
        ----------
        parser: argparse.Parser, required
            The command-line arguments parser.
        """
        parser.add_argument('--input-file',
                            type=str,
                            help="The path of the input file.")

    def handle(self, *args, **options):
        """Import the references."""
        input_file = Path(options['input_file'])
        references = self.__load_references(input_file)
        self.__import_references(references)

    def __import_references(self, references: list[str]):
        """Import the provided references.

        Parameters
        ----------
        references: list of str, required
            The references to insert.
        """
        for ref_text in references:
            ref_text = ref_text.strip()
            if not Reference.objects.filter(text=ref_text).exists():
                Reference.objects.create(text=ref_text, is_approved=True)
                message = self.style.SUCCESS(
                    f"Inserted reference with text '{ref_text}'.")
                self.stdout.write(message)
            else:
                message = self.style.WARNING(
                    f"Reference with text '{ref_text}' already exists.")
                self.stdout.write(message)

    def __load_references(self, input_file: Path) -> list[str]:
        """Load the references from the providef input file.

        Parameters
        ----------
        input_file: Path, required
            The path of the input file.

        Returns
        -------
        references: list of str
            The list of references loaded from the file.
        """
        if not input_file.exists():
            raise CommandError(f"File '{input_file}' does not exist.")

        if not input_file.is_file():
            raise CommandError(f"The path '{input_file}' is not a file.")

        with open(input_file, 'r') as file:
            references = file.readlines()
        return references
