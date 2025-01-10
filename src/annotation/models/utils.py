"""Defines utility methods."""
import re
import unicodedata


def extract_title_word(text: str) -> str | None:
    """Extract the entry from the provided text.

    Parameters
    ----------
    text: str, required
        The text from which to extract the entry.

    Returns
    -------
    entry: str
        The extracted entry, or None.
    """
    match = re.match(r'\*\*[^*]*\*\*', text)
    if match is None:
        return text

    entry = f'{match.group(0).replace("*", "")}'
    entry = entry.replace("^", "")
    return entry


def remove_diacritics(text: str) -> str | None:
    """Remove the diacritics from the given text.

    Parameters
    ----------
    text: str, required
        The text from which to remove diacritics.

    Returns
    -------
    ascii_text: str
        The text without diacritics.
    """
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
