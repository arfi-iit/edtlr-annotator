"""Defines the command for importing data into the database."""
from annotation.models import Volume, Page, Entry, EntryPage
from annotation.utils.xml2edtlrmd import convert_xml_to_edtlr_markdown
from django.core.management.base import BaseCommand
from itertools import takewhile
from pathlib import Path
from typing import List, Dict
import pandas as pd
import re

REPLACEMENT_MAP = str.maketrans("ŞşŢţÅåÁáẤấẮắ", "ȘșȚțAaAaAaAa")
TITLE_WORD_REGEX = r"^\*\*(?P<title_word>[^*]+)\*\*"


class Command(BaseCommand):
    """Implements the command for importing data into the database."""

    help = "Import the data into the database."
    requires_migrations_checks = True

    def add_arguments(self, parser):
        """Add command-line arguments.

        Parameters
        ----------
        parser: argparse.Parser, required
            The command-line arguments parser.
        """
        parser.add_argument(
            '--entries-directory',
            help="The path of the directory containing dictionary entries.",
            required=True)
        parser.add_argument(
            '--images-directory',
            help="The path of the directory containing page images.",
            required=True)
        parser.add_argument(
            '--static-directory',
            help="The path of the directory containing static files.",
            required=True)
        parser.add_argument(
            '--mappings-file',
            help="The file containing mappings between entries and pages.",
            required=True)
        parser.add_argument(
            '--volume',
            help="The name of the volume under which to import the data.",
            default="eDTLR")
        parser.add_argument('--page-offset',
                            help="The page offset.",
                            type=int,
                            default=0)

    def handle(self, *args, **options):
        """Import the data into the database."""
        entries_dir = Path(options['entries_directory'])
        images_dir = Path(options['images_directory'])
        mappings_file = Path(options['mappings_file'])
        static_dir = Path(options['static_directory'])

        images = self.__scan_images(images_dir)
        volume = self.__load_volume(options['volume'])
        mappings = self.__load_mappings(mappings_file)
        pages = self.__create_pages(images, volume, static_dir)

        for entry_file in entries_dir.glob("*.xml"):
            contents = self.__read_contents(entry_file)
            if contents is None:
                error = f'Could not extract title word from file {entry_file}.'
                self.stderr.write(error)
                continue
            title_word, text = contents
            entry = self.__normalize_entry(title_word)
            if entry not in mappings:
                error = f"Could not find page mappings for entry {entry}."
                self.stderr.write(error)
            else:
                offset = 0
                if options['page_offset'] is not None:
                    offset = int(options['page_offset'])
                entry_pages = [p + offset for p in mappings[entry]]
                entry_pages = [
                    pages[page_no] for page_no in entry_pages
                    if page_no in pages
                ]
                self.__import_data(entry_file, text, entry_pages, static_dir)

        self.stdout.write("Finished importing data.")

    def __import_data(self, entry_file: Path, text: str, pages: List[Page],
                      static_directory: Path):
        """Import the data into the database.

        Parameters
        ----------
        entry_file: Path, required
            The path of the file containing the entry to import.
        text: str, required
            The text of the entry.
        pages: list of int, required
            The page numbers of the images to import.
        static_directory: Path, required
            The path of the directory containing static files.
        """
        entry = self.__get_or_create_entry(text)
        message = f"Importing pages {[p.page_no for p in pages]} for entry {entry.title_word}."
        self.stdout.write(message)

        self.__create_or_update_pages(entry, pages)
        self.__mark_imported(entry_file)

    def __create_or_update_pages(self, entry: Entry, pages: List[Page]):
        """Create or update the pages associated with the entry.

        Parameters
        ----------
        entry: Entry, required
            The entry for which to create or update pages.
        pages: list of Page, required
            The list of pages associated with the entry.
        """
        entry_pages = EntryPage.objects.filter(entry=entry)
        for ep in entry_pages:
            ep.delete()

        for page in pages:
            ep = EntryPage(entry=entry, page=page)
            ep.save()

    def __read_contents(self, entry_file: Path) -> tuple[str, str] | None:
        """Read the contents of the entry file.

        Parameters
        ----------
        entry_file: Path, required
            The path of the entry file.

        Returns
        -------
        (title_word, text): tuple of (str, str) or None
            The contents of the entry file.
        """
        with open(entry_file, encoding='utf8') as f:
            contents = f.read()

        text = convert_xml_to_edtlr_markdown(contents)
        match = re.match(TITLE_WORD_REGEX, text, re.MULTILINE | re.UNICODE)
        if match is None:
            return None
        return (match.group(1), text)

    def __get_or_create_entry(self, text: str) -> Entry:
        """Create an entry from the contents of the specified file.

        Parameters
        ----------
        text: str, required
            The text of the entry.

        Returns
        -------
        entry: Entry
            The entry created from the contents of the file.
        """
        entry = Entry.objects.filter(text=text).first()
        if entry is None:
            entry = Entry()
            entry.set_text(text)
            entry.save()

        return entry

    def __mark_imported(self, entry_file: Path):
        """Mark the entry file as imported.

        Parameters
        ----------
        entry_file: Path, required
            The path of the file from which to create an entry.
        """
        imported_dir = entry_file.parent / "imported"
        if not imported_dir.exists():
            imported_dir.mkdir(exist_ok=True)
        new_path = imported_dir / entry_file.name
        entry_file.rename(new_path)

    def __create_pages(self, images: Dict[int, Path], volume: Volume,
                       static_directory: Path) -> Dict[int, Page]:
        """Create the pages.

        Parameters
        ----------
        images: dict of (int, Path), required
            The dictionary mapping the page number to its file path.
        volume: Volume, required
            The volume for which data is imported.
        static_directory: Path, required
            The path of the directory containing static files.

        Returns
        -------
        page_list: list of Page
            The list of inserted pages.
        """
        pages = {}
        for (page_no, image_path) in images.items():
            page = self.__create_or_update_page(page_no, volume, image_path,
                                                static_directory)
            pages[page.page_no] = page

        return pages

    def __create_or_update_page(self, page_no: int, volume: Volume,
                                image_path: Path, static_dir: Path) -> Page:
        """Create a page or update the page with the specified data.

        Parameters
        ----------
        page_no: int, required
            The number of the page in the volume.
        volume: Volume, required
            The volume which contains the page.
        image_path: Path, required
            The path of the page scan.
        static_dir: Path, required
            The path of the static directory.

        Returns
        -------
        page: Page
            The page object.
        """
        p = Page.objects.filter(volume=volume, page_no=page_no).first()
        page_path = image_path.relative_to(static_dir)
        if p is None:
            p = Page(volume=volume, page_no=page_no, image_path=str(page_path))
        else:
            p.image_path = str(page_path)

        p.save()
        return p

    def __load_volume(self, volume_name: str) -> Volume:
        """Load or insert the volume with the specified name.

        Parameters
        ----------
        volume_name: str, required
            The name of the volume.

        Returns
        -------
        volume: Volume
            The volume with the specified name.
        """
        volume = Volume.objects.filter(name=volume_name)\
                               .first()
        if volume is None:
            volume = Volume(name=volume_name)
            volume.save()
        return volume

    def __scan_images(self,
                      directory: Path,
                      extension: str = "png") -> Dict[int, Path]:
        """Scan the provided diectory for imges.

        Parameters
        ----------
        directory: Path, required
            The path of the directory to scan.
        extension: str, optional
            The extension of the images.
        """
        results = {}
        for img in directory.glob(f'*.{extension}'):
            self.stdout.write(str(img))
            match = re.search(r'\d+', img.stem)
            if match:
                results[int(match.group())] = img
        return results

    def __load_mappings(self, mappings_file: Path) -> Dict[str, List[int]]:
        """Load the entry-page mappings from the provided file.

        Parameters
        ----------
        mappings_file: Path, required
            The path of the CSV file from which to load the mapping.

        Returns
        -------
        mappings: dict of (str, list of str) tuples
            The mappings as a dict with the entry as the key, and the list of page numbers as values.
        """
        df = pd.read_csv(mappings_file,
                         header=None,
                         names=['entry', 'pages'],
                         na_values='',
                         dtype=str)
        result = {}
        for row in df.itertuples():
            entry, *_ = row.entry.split()
            if len(str(row.pages)) == 0:
                continue

            pages = [int(num) for num in row.pages.split(',')]
            entry = self.__normalize_entry(entry)
            if entry in result:
                s1 = set(result[entry])
                s2 = set(pages)
                result[entry] = list(s1.union(s2))
            else:
                result[entry] = list(set(pages))

        return result

    def __normalize_entry(self, entry: str) -> str:
        """Remove problematic characters from the given entry.

        Parameters
        ----------
        entry: str, required
            The entry to sanitize.

        Returns
        -------
        canonical_entry: str
            The normalized entry.
        """
        if entry is None:
            return ""
        entry = entry.strip()
        if len(entry) == 0:
            return ""

        entry, *_ = entry.split()
        entry = entry.upper()
        entry = entry.translate(REPLACEMENT_MAP)
        letters = [
            letter for letter in takewhile(lambda c: c.isalpha(), entry)
        ]
        canonical_entry = ''.join(letters)
        return canonical_entry
