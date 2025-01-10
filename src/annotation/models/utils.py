import re


def extract_entry(text: str) -> str | None:
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
