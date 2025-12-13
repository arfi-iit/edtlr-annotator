"""The view for saving an annotation."""
from typing import Tuple

from annotation.models.annotation import Annotation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils import timezone
from django.views import View


class SaveAnnotationView(LoginRequiredMixin, View):
    """Implements the view for saving an annotation."""

    annotate_page = 'annotation:annotate'
    index_page = "annotation:index"

    def post(self, request):
        """Save the annotation from the request body.

        Parameters
        ----------
        request: HttpRequest, required
            The HTTP request object.
        """
        entry_id, text = self.__parse_request_body(request)
        annotation = Annotation.objects.get(entry=entry_id, user=request.user)
        # The `get()` method throws a `DoesNoExist` exception if the annotation is not found
        self.__update_annotation(annotation, text)
        return redirect(self.annotate_page, id=annotation.id)

    def __update_annotation(self, annotation: Annotation, text: str):
        annotation.set_text(text)
        annotation.row_update_timestamp = timezone.now()
        annotation.status = Annotation.AnnotationStatus.IN_PROGRESS
        annotation.save()

    def __parse_request_body(self, request) -> Tuple[int, HttpRequest]:
        text = request.POST['text']
        entry_id = int(request.POST['entry-id'])
        return entry_id, text
