"""Defines the command for shifting the pages of the entries of a dictionary volume."""
from django.core.management.base import BaseCommand
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
        try:
            volume = Volume.objects.get(name=volume_name,
                                        dictionary__name=dictionary_name)
        except Volume.DoesNotExist:
            message = self.style.ERROR(
                f'The volume {volume_name} does not exist in dictionary {dictionary_name}.'
            )
            self.stdout.write(message)
            return

        pages_by_no, pages_by_id = {}, {}
        for page in Page.objects.filter(volume=volume):
            pages_by_no[page.page_no] = page
            pages_by_id[page.id] = page

        entry_pages = list(EntryPage.objects.filter(page__volume=volume)\
                           .order_by('entry_id'))
        for ep in entry_pages:
            current_page = pages_by_id[ep.page_id]
            new_page = pages_by_no[current_page.page_no + page_offset]
            entry = ep.entry
            message = self.style.NOTICE(
                f"Shifting ({ep.entry}, {ep.page}) to ({ep.entry}, {new_page})."
            )
            self.stdout.write(message)
            if EntryPage.objects.filter(entry=ep.entry,
                                        page=new_page).exists():
                message = self.style.NOTICE(
                    f"Entry ({ep.entry}, {ep.page}) already exists.")
                self.stdout.write(message)
            else:
                ep.delete()
                ep = EntryPage(entry=entry, page=new_page)
                ep.save()
