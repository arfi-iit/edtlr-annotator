"""The view for retrieving entry contents."""
from ..models.annotation import Annotation
from ..models.entry import Entry
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import JsonResponse
from django.views import View


class GetEntryContentsView(LoginRequiredMixin, View):
    """Implements the view for retrieving the contents of the specified entry."""

    def get(self, request, entry_id: int) -> JsonResponse | Http404:
        """Retrieve the contents for the specified entry.

        Parameters
        ----------
        request: HttpRequest, required
            The HttpRequest object.
        entry_id: int, required
            The id of the entry for which to load the data.

        Returns
        -------
        response: JsonResponse or Http404
            The response data.
            If the response is a JsonResponse, then it contains the following fields:
            - 'contents': the text of the entry
        """
        try:
            entry = Entry.objects.get(pk=entry_id)
            annotation = Annotation.objects.filter(entry=entry,
                                                   user=request.user).first()

            data = {'text': annotation.text}
            return JsonResponse(data)
        except (Annotation.DoesNotExist):
            raise Http404()
