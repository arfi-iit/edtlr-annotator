"""The view for a new annotation."""
from ..models.annotation import Annotation
from ..models.entry import Entry
from ..models.entrypage import EntryPage
from ..models.page import Page
from .viewsettings import MAX_CONCURRENT_ANNOTATORS
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import redirect
from django.views import View


class NewAnnotationView(LoginRequiredMixin, View):
    """Implements the view for creating a new annotation."""

    annotate_page = 'annotation:annotate'
    thank_you_page = 'annotation:thank-you'

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
        status = Annotation.AnnotationStatus.IN_PROGRESS
        record = Annotation(entry=entry, user=user, status=status)
        record.set_text(entry.text)
        record.save()
        return record
