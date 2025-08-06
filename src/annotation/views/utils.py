"""Defines utility methods for views."""
from annotation.models.page import Page
from annotation.apps import AnnotationConfig


def get_image_path(page: Page | None) -> str:
    """Get the image path of the specified page.

    Parameters
    ----------
    page: Page, required
        The page for which to get the image path.

    Returns
    -------
    image_path: str or None
        The image path of the image, or None if the page is None.
    """
    if page is None:
        return None
    return f'/{AnnotationConfig.name}/{page.image_path}'
