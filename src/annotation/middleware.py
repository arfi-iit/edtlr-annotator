"""Module for custom middleware."""
from django.urls import set_script_prefix


class RoutePrefixMiddleware:
    """Adds a prefix to routes."""

    def __init__(self, get_response):
        """Initialize the middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Call the middleware."""
        script_name = request.META.get('X-Annotate-Base-Url', '')

        if script_name and request.path_info.startswith(script_name):
            request.path_info = request.path_info[len(script_name):]
            set_script_prefix(script_name)

        response = self.get_response(request)
        return response
