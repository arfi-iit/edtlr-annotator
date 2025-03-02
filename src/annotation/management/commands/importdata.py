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

    def handle(self, *args, **options):
        """Import the data into the database."""
        entries_dir = Path(options['entries_directory'])
        images_dir = Path(options['images_directory'])
        mappings_file = Path(options['mappings_file'])
        static_dir = Path(options['static_directory'])
        images = self.__scan_images(images_dir)

        mappings = self.__load_mappings(mappings_file)
        for entry_file in entries_dir.glob("*.xml"):
            entry = self.__normalize_entry(entry_file.stem)
            if entry not in mappings:
                error = f"Could not find page mappings for entry {entry}."
                self.stderr.write(error)
            else:
                volume_name = options['volume']
                pages = mappings[entry]
                self.__import_data(entry_file, pages, images, volume_name,
                                   static_dir)

        self.stdout.write("Finished importing data.")

    def __import_data(self, entry_file: Path, pages: List[int],
                      images: Dict[int, Path], volume_name: str,
                      static_directory: Path):
        """Import the data into the database.

        Parameters
        ----------
        entry_file: Path, required
            The path of the file containing the entry to import.
        pages: list of int, required
            The page numbers of the images to import.
        images: dict of (int, Path), required
            The page images as a dictionary of (page number, Path).
        volume_name: str, required
            The name of the parent volume.
        static_directory: Path, required
            The path of the directory containing static files.
        """
        message = f"Importing pages {pages} for entry {str(entry_file)}."
        self.stdout.write(message)

        for page_no in pages:
            if page_no not in images:
                message = f'No image found for page {page_no}. Import will not run.'
                self.stderr.write(message)
                return

        pages_ = self.__create_pages(pages, images, volume_name,
                                     static_directory)

        entry = self.__create_entry(entry_file)
        for page in pages_:
            ep = EntryPage(entry=entry, page=page)
            ep.save()

    def __create_entry(self, entry_file: Path) -> Entry:
        """Create an entry from the contents of the specified file.

        Parameters
        ----------
        entry_file: Path, required
            The path of the file from which to create an entry.

        Returns
        -------
        entry: Entry
            The entry created from the contents of the file.
        """
        with open(entry_file, encoding='utf8') as f:
            contents = f.read()

        entry = Entry()
        entry.set_text(convert_xml_to_edtlr_markdown(contents))
        entry.save()
        imported_dir = entry_file.parent / "imported"
        if not imported_dir.exists():
            imported_dir.mkdir(exist_ok=True)
        new_path = imported_dir / entry_file.name
        entry_file.rename(new_path)

        return entry

    def __create_pages(self, pages: List[int], images: Dict[int, Path],
                       volume_name: str, static_directory: Path) -> List[Page]:
        """Create the pages.

        Parameters
        ----------
        pages: list of int, required
            The collection of page numbers for which to create pages.
        images: dict of (int, Path), required
            The dictionary mapping the page number to its file path.
        volume_name: str, required
            The name of the volume.
        static_directory: Path, required
            The path of the directory containing static files.

        Returns
        -------
        page_list: list of Page
            The list of inserted pages.
        """
        volume = self.__load_volume(volume_name)

        def load_or_create_page(page_no, images, volume):
            p = Page.objects.filter(volume=volume, page_no=page_no)\
                            .first()
            if p is None:
                path = images[page_no]
                page_path = path.relative_to(static_directory)
                p = Page(volume=volume,
                         page_no=page_no,
                         image_path=str(page_path))
                p.save()

            return p

        return [load_or_create_page(p, images, volume) for p in pages]

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
