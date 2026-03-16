"""The view for a new annotation."""
from annotation.models.annotation import Annotation
from annotation.models.entry import Entry
from annotation.models.entrypage import EntryPage
from annotation.models.page import Page
from annotation.models.reference import Reference
from annotation.utils.automaticannotation import ReferenceAnnotator
from annotation.utils.automaticannotation import apply_preprocessing
from annotation.utils.xml2edtlrmd import remove_annotation_marks
from annotation.views.viewsettings import APPLICATION_MODE
from annotation.views.viewsettings import AUTOMATIC_REFERENCE_ANNOTATION
from annotation.views.viewsettings import ApplicationModes
from annotation.views.viewsettings import MAX_CONCURRENT_ANNOTATORS
from annotation.views.viewsettings import PRESERVE_ENTRY_TEXT
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Count
from django.shortcuts import redirect
from django.views import View
import random


class NewAnnotationView(LoginRequiredMixin, View):
    """Implements the view for creating a new annotation."""

    annotate_page = 'annotation:annotate'
    thank_you_page = 'annotation:thank-you'

    @property
    def references(self):
        """Get the collection of references."""
        CACHE_KEY = 'references'
        CACHE_TIMEOUT = 3600

        refs = cache.get(CACHE_KEY)
        if refs is None:
            print("Loading all references.")
            refs = Reference.objects\
                            .filter(is_approved=True)\
                            .values_list('text', flat=True)
            refs = list(refs)
            cache.set(CACHE_KEY, refs, CACHE_TIMEOUT)
        return refs

    def get(self, request):
        """Handle the GET request.

        Parameters
        ----------
        request: HttpRequest, required
            The request object.
        """
        entry = self.__get_next_entry(request.user)
        if entry is not None:
            annotation = self.__insert_annotation(request.user, entry)
            return redirect(self.annotate_page, id=annotation.id)

        return redirect(self.thank_you_page)

    def __get_next_entry(self, user: User) -> Page | None:
        """Get next entry to annotate.

        Parameters
        ----------
        user: User, required
            The request user.

        Returns
        -------
        entry: Entry
            The next entry to annotate.
        """
        entries_from_active_dictionary = Entry.objects.filter(entrypage__page__volume__dictionary__is_active=True)
        next_entries = entries_from_active_dictionary.exclude(annotation__user=user)\
                                                     .annotate(annotation_count=Count('annotation', distinct=True))\
                                                     .filter(annotation_count__lt=MAX_CONCURRENT_ANNOTATORS)\
                                                     .distinct()
        next_entry = next_entries.first()
        if next_entry is not None:
            return next_entry
        next_entry = entries_from_active_dictionary.distinct().first()
        return next_entry

    def __insert_annotation(self, user: User, entry: Entry) -> Annotation:
        """Create a new annotation for the specified entry and user.

        Parameters
        ----------
        user: User, required
            The annotation user.
        entry: Entry, required
            The entry of the annotation.

        Returns
        -------
        annotation: Annotation
            The new annotation.
        """
        record = AnnotationFactory.create(user, entry, self.references)
        record.save()
        return record


class AnnotationFactory:
    """Creates annotation instances."""

    MIN_LEN_DIFF_FOR_RANDOMIZATION = 5
    MULTIPLE_EDITS_THRESHOLD = 100
    NUM_EDITS_BEFORE_THRESHOLD = 1
    NUM_EDITS_AFTER_THRESHOLD = 5

    @staticmethod
    def create(user: User, entry: Entry, references: list[str]) -> Annotation:
        """Create a new annotation for the specified entry and user.

        Parameters
        ----------
        user: User, required
            The annotation user.
        entry: Entry, required
            The entry of the annotation.
        references: list of str, required
            The list of references to identify from the entry text.

        Returns
        -------
        annotation: Annotation
            The new annotation.
        """
        status = Annotation.AnnotationStatus.IN_PROGRESS
        record = Annotation(entry=entry, user=user, status=status)

        match APPLICATION_MODE:
            case ApplicationModes.CorrectAnnotatedEntries:
                text = apply_preprocessing(entry.text)
                text = AnnotationFactory.randomize_text(text, entry.title_word)
                if AUTOMATIC_REFERENCE_ANNOTATION:
                    annotator = ReferenceAnnotator(references)
                    text = annotator.annotate(text)
            case ApplicationModes.AnnotateOcrText:
                text = apply_preprocessing(entry.text)
                text = remove_annotation_marks(text)
                text = AnnotationFactory.randomize_text(text, entry.title_word)
            case _:
                text = f'**{entry.title_word}**'
        record.set_text(text)

        record.title_word = entry.title_word
        record.title_word_normalized = entry.title_word_normalized
        record.version = 1

        return record

    @staticmethod
    def randomize_text(text: str, title_word: str) -> str:
        """Apply random deletions to the annotation text.

        This method randomly deletes several characters from the given text,
        in order to make the initial text of the annotations of the same entry
        different from each other. The method returns the same text if the flag
        `PRESERVE_ENTRY_TEXT` is set to `True`.

        Parameters
        ----------
        text: str, required
            The text to which postprocessing should be applied.
        title_word: str, required
            The title-word of the entry.

        Returns
        -------
        post_processed_text: str
            The text after post processing.
        """
        if PRESERVE_ENTRY_TEXT:
            return text

        text = text if text is not None else ''
        formatted_title_word = f'**{title_word}**' if title_word is not None else ''

        len_diff = len(text) - len(formatted_title_word)
        if len_diff < AnnotationFactory.MIN_LEN_DIFF_FOR_RANDOMIZATION:
            return text

        num_edits = AnnotationFactory.NUM_EDITS_BEFORE_THRESHOLD
        if len_diff < AnnotationFactory.MULTIPLE_EDITS_THRESHOLD:
            num_edits = AnnotationFactory.NUM_EDITS_AFTER_THRESHOLD
        random.seed()
        for _ in range(num_edits):
            idx = random.randint(len(formatted_title_word), len(text) - 1)
            text = text[:idx] + text[idx + 1:]
        return text
