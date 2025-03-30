"""The view for marking an annotation as complete."""
from ..models.annotation import Annotation
from .viewsettings import MAX_CONCURRENT_ANNOTATORS
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views import View
from typing import Tuple


class MarkAnnotationCompleteView(LoginRequiredMixin, View):
    """Implements the view for marking an annotation as being complete."""

    index_page = "annotation:index"

    def post(self, request):
        """Save the annotation from the request body and mark it as complete."""
        entry_id, contents = self.__parse_request_body(request)
        self.__mark_annotation_complete(entry_id, contents, request.user)
        self.__check_conflicts(entry_id)
        return redirect(self.index_page)

    def __check_conflicts(self, entry_id: int):
        entry_annotations = Annotation.objects.filter(
            entry=entry_id, status=Annotation.AnnotationStatus.COMPLETE)
        if len(entry_annotations) < MAX_CONCURRENT_ANNOTATORS:
            return

        if self.__have_conflicts(entry_annotations):
            for annotation in entry_annotations:
                annotation.version = annotation.version + 1
                annotation.status = Annotation.AnnotationStatus.CONFLICT
                annotation.save()

    def __have_conflicts(self, entry_annotations) -> bool:
        iterator = iter(entry_annotations)

        first = next(iterator).text
        for item in iterator:
            if first != item.text:
                return True

        return False

    def __mark_annotation_complete(self, entry_id: int, text: str, user: User):
        annotation = Annotation.objects.get(
            entry=entry_id,
            user=user,
            status=Annotation.AnnotationStatus.IN_PROGRESS)

        if annotation is not None:
            annotation.set_text(text)
            annotation.status = Annotation.AnnotationStatus.COMPLETE
            annotation.save()

    def __parse_request_body(self, request) -> Tuple[int, object]:
        text = request.POST['text']
        entry_id = int(request.POST['entry-id'])
        return entry_id, text
