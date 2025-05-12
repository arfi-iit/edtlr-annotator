"""The view for a new annotation."""
from annotation.models.annotation import Annotation
from annotation.models.entry import Entry
from annotation.models.entrypage import EntryPage
from annotation.models.page import Page
from annotation.models.reference import Reference
from annotation.utils.automaticannotation import ReferenceAnnotator
from annotation.utils.automaticannotation import apply_preprocessing
from annotation.views.viewsettings import MAX_CONCURRENT_ANNOTATORS
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Count
from django.shortcuts import redirect
from django.views import View


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
        in_progress_annotations = Annotation.objects.values('entry')\
                                                    .annotate(count=Count('entry'))\
                                                    .order_by('entry')\
                                                    .filter(count__lt=MAX_CONCURRENT_ANNOTATORS)

        user_annotations = Annotation.objects.filter(user=user)\
                                             .values('entry')
        user_annotations = set([a['entry'] for a in user_annotations])

        for annotation in in_progress_annotations:
            entry_id = annotation['entry']
            if entry_id not in user_annotations:
                return Entry.objects.get(pk=entry_id)

        in_progress_entries = [
            p['entry'] for p in Annotation.objects.values('entry')
        ]

        valid_ids = [
            ep['entry_id'] for ep in EntryPage.objects.values('entry_id')
        ]

        return Entry.objects.exclude(id__in=in_progress_entries)\
            .filter(id__in=valid_ids)\
            .first()

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
        status = Annotation.AnnotationStatus.IN_PROGRESS
        record = Annotation(entry=entry, user=user, status=status)
        annotator = ReferenceAnnotator(self.references)
        text = annotator.annotate(apply_preprocessing(entry.text))
        record.set_text(text)
        record.save()
        return record
