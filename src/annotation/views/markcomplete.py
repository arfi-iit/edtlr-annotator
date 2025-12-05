"""The view for marking an annotation as complete."""
from typing import Tuple
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from annotation.models.annotation import Annotation
from annotation.models.entry import Entry
from annotation.utils.xml2edtlrmd import Marks
from annotation.views.viewsettings import MAX_CONCURRENT_ANNOTATORS


class MarkAnnotationCompleteView(LoginRequiredMixin, View):
    """Implements the view for marking an annotation as being complete."""

    index_page = "annotation:index"
    annotate_page = "annotation:annotate"

    def post(self, request):
        """Save the annotation from the request body and mark it as complete."""
        entry_id, contents = self.__parse_request_body(request)
        is_valid, error = self.__validate(contents, entry_id)
        if not is_valid:
            annotation = Annotation.objects.get(entry=entry_id,
                                                user=request.user)
            self.__update_annotation(annotation, contents)
            messages.error(request, error, extra_tags="danger")
            return redirect(self.annotate_page, id=annotation.id)
        self.__mark_annotation_complete(entry_id, contents, request.user)
        self.__check_conflicts(entry_id)
        return redirect(self.index_page)

    def __validate(self, text: str, entry_id: int) -> Tuple[bool, str | None]:
        entry = Entry.objects.get(id=entry_id)
        formatted_headword = f'{Marks.BOLD}{entry.title_word_normalized}{Marks.BOLD}'
        content_length = len(text) if text is not None else 0
        if content_length <= len(formatted_headword):
            return (False, _("Entry text is too short."))
        return (True, None)

    def __check_conflicts(self, entry_id: int):
        entry_annotations = Annotation.objects.filter(entry=entry_id)\
            .exclude(status=Annotation.AnnotationStatus.IN_PROGRESS)
        if len(entry_annotations) < MAX_CONCURRENT_ANNOTATORS:
            return

        status = Annotation.AnnotationStatus.COMPLETE
        if self.__have_conflicts(entry_annotations):
            status = Annotation.AnnotationStatus.CONFLICT

        for annotation in entry_annotations:
            annotation.version = annotation.version + 1
            annotation.status = status
            annotation.save()

    def __have_conflicts(self, entry_annotations) -> bool:
        iterator = iter(entry_annotations)

        first = next(iterator).text
        for item in iterator:
            if first != item.text:
                return True

        return False

    def __mark_annotation_complete(self, entry_id: int, text: str, user: User):
        annotation = Annotation.objects.get(entry=entry_id, user=user)
        self.__update_annotation(annotation, text,
                                 Annotation.AnnotationStatus.COMPLETE)

    def __update_annotation(self,
                            annotation: Annotation,
                            text: str,
                            status: Annotation.AnnotationStatus = None):

        annotation.set_text(text)
        if status is not None:
            annotation.status = status
        annotation.row_update_timestamp = timezone.now()
        annotation.version += 1
        annotation.save()

    def __parse_request_body(self, request) -> Tuple[int, object]:
        text = request.POST['text']
        entry_id = int(request.POST['entry-id'])
        return entry_id, text
