"""Defines the command for shifting the pages of the entries of a dictionary volume."""
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from annotation.models import EntryPage
from annotation.models import Volume
from annotation.models import Page


class Command(BaseCommand):
    """Implements the command for shifting the entry pages."""

    help = "Shift entry pages with the specified offset."

    def add_arguments(self, parser):
        """Add command-line arguments.

        Parameters
        ----------
        parser: argparse.Parser, required
            The arguments parser.
        """
        parser.add_argument('--dictionary',
                            type=str,
                            help="The name of the dictionary.",
                            required=True)
        parser.add_argument('--volume',
                            type=str,
                            help="The name of the dictionary volume.",
                            required=True)
        parser.add_argument('--page-offset',
                            type=int,
                            help="The page offset.",
                            default=0)

    def handle(self, *args, **kwargs):
        """Shift the entry pages."""
        dictionary_name = kwargs['dictionary']
        volume_name = kwargs['volume']
        page_offset = int(kwargs['page_offset'])
        volume = self.__load_volume(volume_name, dictionary_name)
        pages_by_no = self.__load_page_map(volume)

        for ep in self.__load_entry_pages(volume):
            current_page = ep.page
            page_no = current_page.page_no + page_offset
            if page_no not in pages_by_no:
                message = self.style.WARNING(
                    f"There is no page with number {page_no}; skipping.")
                self.stdout.write(message)
                continue

            new_page = pages_by_no[page_no]
            entry = ep.entry
            message = self.style.NOTICE(
                f"Shifting ({ep.entry}, {ep.page}) to ({ep.entry}, {new_page})."
            )
            self.stdout.write(message)
            if EntryPage.objects.filter(entry=ep.entry,
                                        page=new_page).exists():
                message = self.style.NOTICE(
                    f"Entry ({ep.entry}, {new_page}) already exists.")
                self.stdout.write(message)
            else:
                ep.delete()
                ep = EntryPage(entry=entry, page=new_page)
                ep.save()

    def __load_entry_pages(self, volume: Volume) -> list[EntryPage]:
        """Load the entry pages for the specified volume."""
        entry_pages = [
            ep for ep in EntryPage.objects.filter(page__volume=volume).
            select_related('entry', 'page').order_by('entry_id')
        ]
        return entry_pages

    def __load_page_map(self, volume: Volume) -> dict[int, Page]:
        """Load the collection that maps page numbersn to the pages.

        Parameters
        ----------
        volume: Volume, required
            The volume for which to load the page maps.

        Returns
        -------
        pages_by_no: dict(int, Page)
            The dict containing the mappings between page number and page.
        """
        pages_by_no = {}
        for page in Page.objects.filter(volume=volume):
            pages_by_no[page.page_no] = page
        return pages_by_no

    def __load_volume(self, volume_name: str, dictionary_name: str) -> Volume:
        """Load the volume specified by name and dictionary name."""
        try:
            volume = Volume.objects.get(name=volume_name,
                                        dictionary__name=dictionary_name)
            return volume
        except Volume.DoesNotExist:
            raise CommandError(
                f'The volume {volume_name} does not exist in dictionary {dictionary_name}.',
                returncode=1)
