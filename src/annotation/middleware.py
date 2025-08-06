"""Module for custom middleware."""
from django.urls import set_script_prefix
import re


class RoutePrefixMiddleware:
    """Adds a prefix to routes."""

    REQUEST_HEADER = 'HTTP_X_ANNOTATE_BASE_URL'

    def __init__(self, get_response):
        """Initialize the middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Call the middleware."""
        script_name = request.META.get(self.REQUEST_HEADER, '')
        path_info = request.path_info
        if self.__is_valid(script_name) and path_info.startswith(script_name):
            request.path_info = request.path_info[len(script_name):]
            set_script_prefix(script_name)

        response = self.get_response(request)
        return response

    def __is_valid(self, script_name: str) -> bool:
        """Check whether the provided script name is valid.

        Parameters
        ----------
        script_name: str, required
            The script name to validate.

        Returns
        -------
        is_valid: bool
            True if the script name consists only of letters, digits
            and separators ('-', '_', '/'); False otherwise.
        """
        if len(script_name) == 0:
            return False
        if '\n' in script_name or '\r' in script_name or '..' in script_name:
            return False

        return re.fullmatch(r"\/[a-zA-z]([a-zA-Z0-9/\-_]+)?(\/)?",
                            script_name) is not None
