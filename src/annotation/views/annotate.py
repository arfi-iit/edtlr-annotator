"""The view for annotating an entry."""
from ..models.annotation import Annotation
from ..models.entry import Entry
from ..models.entrypage import EntryPage
from .utils import get_image_path
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View


class AnnotateView(LoginRequiredMixin, View):
    """Implements the annotation view."""

    template_name = "annotation/annotate.html"
    thank_you_page = 'annotation:thank-you'
    index_page = 'annotation:index'

    def get(self, request, id: int):
        """Handle the GET request.

        Parameters
        ----------
        request: HttpRequest, required
            The request object.
        id: int, required
            The id of the annotation.
        """
        user_id = request.user.id
        current_annotation = self.__get_in_progress_annotation(user_id, id)
        if current_annotation is not None:
            return render(request,
                          self.template_name,
                          context=self.__build_template_context(
                              current_annotation.entry))
        else:
            return redirect(self.index_page)

    def __build_template_context(self, entry: Entry) -> dict:
        entry_pages = EntryPage.objects.filter(entry=entry)
        pages = sorted([e.page for e in entry_pages], key=lambda p: p.page_no)
        page_images = [get_image_path(p) for p in pages]
        return {'entry_id': entry.id, 'page_images': page_images}

    def __get_in_progress_annotation(self, user_id: int,
                                     annotation_id: int) -> Annotation | None:
        status = Annotation.AnnotationStatus.IN_PROGRESS
        return Annotation.objects.filter(user_id=user_id, status=status, id=annotation_id)\
                                 .first()
