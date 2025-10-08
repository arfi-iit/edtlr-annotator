"""Defines a command to export complete entries."""
from django.core.management.base import BaseCommand
from django.db.models import Count
from annotation.models.annotation import Annotation
import itertools
import hashlib
import os
from pathlib import Path
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import indent


class Command(BaseCommand):
    """Implements the command for exporting complete entries."""

    help = "Exports Annotation models with status 'Complete' to XML files"

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
        parser.add_argument('--output-dir',
                            type=str,
                            default='/tmp/edtlr/export/entries/')

    def handle(self, *args, **options):
        """Export complete entries."""
        batch_size = options['batch_size']
        output_dir = options['output_dir']
        if not os.path.exists(output_dir):
            message = self.style.NOTICE(f'Creating directory {output_dir}.')
            self.stdout.write(message)
            os.makedirs(output_dir)

        entry_ids = self.__load_complete_entries()
        for batch in self.__chunk(entry_ids, batch_size):
            data = self.__load_data(batch)
            self.__export_entries(output_dir, data)

    def __export_entries(self, output_dir: str, data: dict[int, tuple]):
        """Export the entries into the output directory.

        Parameters
        ----------
        output_dir: str, required
            The path of the output directory.
        data: dict of (int, (str, str, str)), required
            The entries to export.
        """
        for entry_id, val in data.items():
            title_word, title_word_normalized, text = val
            entry = self.__build_entry(entry_id, title_word,
                                       title_word_normalized, text)
            file_path = self.__get_entry_file_path(output_dir,
                                                   title_word_normalized,
                                                   entry_id)
            self.__write_entry(entry, file_path)

    def __write_entry(self, entry: ElementTree, file_path: Path):
        """Write the provided entry to the specified file.

        Parameters
        ----------
        entry: ElementTree, required
            The entry to write.
        file_path: Path, required
            The path of the file where to save the entry.
        """
        try:
            indent(entry.getroot())
            entry.write(file_path, xml_declaration=True, encoding='UTF-8')
        except (FileNotFoundError, AttributeError) as ex:
            style = self.style.ERROR
            self.stderr.write(f'Error saving entry to file {file_path}. {ex}',
                              style)

    def __get_entry_file_path(self, output_dir: str, title_word: str,
                              entry_id: int) -> Path:
        """Build the file path of the entry from the specified parameters.

        Parameters
        ----------
        output_dir: str, required
            The path of the output directory.
        title_word: str, required
            The title word of the entry.
        entry_id: int, required
            The id of the entry.

        Returns
        -------
        file_path: Path
            The path of the entry file.
        """
        return Path(output_dir) / Path(f'{title_word}-{entry_id}.xml')

    def __build_entry(self, entry_id: int, title_word: str,
                      title_word_normalized: str, text: str) -> ElementTree:
        """Build the element tree that represents the entry.

        Parameters
        ----------
        entry_id: int, required
            The id of the entry.
        title_word: str, required
            The title word.
        title_word_normalized: str, required
            The normalized form of the title word.
        text: str, required
            The text of the entry.

        Returns
        -------
        entry: ElementTree
            The element tree that represents the entry.
        """
        entry_elem = Element("entry", id=str(entry_id))
        entry_elem.set('xmlns:edtlr', 'https://edtlr.iit.academiaromana-is.ro')

        tw_elem = Element("titleWord",
                          md5hash=self.__compute_md5_hash(title_word))
        tw_elem.text = title_word
        entry_elem.append(tw_elem)

        twn_elem = Element(
            'titleWordNormalized',
            md5hash=self.__compute_md5_hash(title_word_normalized))
        twn_elem.text = title_word_normalized
        entry_elem.append(twn_elem)
        body_elem = Element("body", md5hash=self.__compute_md5_hash(text))
        for line in text.splitlines():
            paragraph_elem = Element("paragraph")
            paragraph_elem.text = line
            body_elem.append(paragraph_elem)
        entry_elem.append(body_elem)

        return ElementTree(entry_elem)

    def __chunk(self, collection, batch_size: int):
        """Split the specified collection into batches.

        Parameters
        ----------
        collection: iterable, required
            The collection to split.
        batch_size: int, required
            The number of items in each batch.

        Returns
        -------
        batches: generator
            The generator that returns each batch.
        """
        iterator = iter(collection)
        while batch := list(itertools.islice(iterator, batch_size)):
            yield batch

    def __load_data(self,
                    entry_ids: list[int]) -> dict[int, tuple[str, str, str]]:
        """Load the data of the specified entries.

        Parameters
        ----------
        entry_ids: list of int, required
            The ids of the entries for which to load data.

        Returns
        -------
        data: dictionary of (entry_id, entry_data)
            The data of the entries.
        """
        data = Annotation.objects\
            .filter(entry_id__in=entry_ids)\
            .values_list('entry_id', 'text', 'title_word', 'title_word_normalized')
        return {entry_id: (tw, twn, text) for entry_id, text, tw, twn in data}

    def __load_complete_entries(self) -> list[int]:
        """Load the ids of the entries which have all annotations complete.

        Returns
        -------
        entry_ids: list of int
            The list of ids of the complete entries.
        """
        complete_entries = Annotation.objects.filter(status='Complete') \
                                             .values('entry_id') \
                                             .annotate(entry_count=Count('entry_id')) \
                                             .filter(entry_count__gt=1) \
                                             .values_list('entry_id', flat=True)
        return list(complete_entries)

    def __compute_md5_hash(self, value: str) -> str:
        """Compute the MD5 hash of the provided value.

        Parameters
        ----------
        value: str, required
            The value for which to compute the hash.

        Returns
        -------
        hash_str: str
            The hash string.
        """
        algorithm = hashlib.md5
        return algorithm(value.encode('utf-8')).hexdigest()
