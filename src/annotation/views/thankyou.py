"""The view that is displayed when there are no more entries to annotate."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class ThankYouView(LoginRequiredMixin, View):
    """Implements the view that displays a thank you message when there are no entries to annotate."""

    template_name = "annotation/thank-you.html"

    def get(self, request):
        """Handle the GET request.

        Parameters
        ----------
        request: HttpRequest, required
            The request object.
        """
        return render(request, self.template_name)
