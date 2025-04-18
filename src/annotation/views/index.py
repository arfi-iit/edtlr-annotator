"""The index view."""
from annotation.models.annotation import Annotation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class IndexView(LoginRequiredMixin, View):
    """Implements the index view."""

    template_name = "annotation/index.html"

    def get(self, request):
        """Handle the GET request.

        Parameters
        ----------
        request: HttpRequest, required
            The request object.
        """
        annotations = Annotation.objects\
            .filter(user=request.user)\
            .order_by('-row_update_timestamp')
        annotations = [(a.id, a.title_word,
                        Annotation.AnnotationStatus(a.status).label,
                        a.status != Annotation.AnnotationStatus.COMPLETE)
                       for a in annotations]

        return render(request,
                      self.template_name,
                      context={'annotations': annotations})
