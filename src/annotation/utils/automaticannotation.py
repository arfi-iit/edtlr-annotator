"""Automatic annotation of entry texts."""
import ahocorasick
from annotation.utils.xml2edtlrmd import Marks
from collections import namedtuple

TextRef = namedtuple('TextRef', ['start_index', 'end_index', 'reference'])


class ReferenceAnnotator:
    """This class implements the automatic annotation of references."""

    def __init__(self, references: list[str]):
        """Create a new instance of the class.

        Parameters
        ----------
        references: list of str, required
            The list of references.
        """
        self.__references = references if references is not None else []
        self.__automaton = self.__make_automaton()

    def annotate(self, text: str) -> str:
        """Annotate the references in the specified text.

        Parameters
        ----------
        text: str, required
            The text to annotate.

        Returns
        -------
        annotated_text: str
            The annotated text.
        """
        if len(self.__references) == 0:
            return text

        text = text.replace(Marks.REFERENCE, "")
        found_refs = self.__search_references(text)
        found_refs.sort(key=lambda ref: ref.start_index)
        merged = self.__merge_overlaps(found_refs)
        return self.__apply_anotation(text, merged)

    def __apply_anotation(self, text: str, references: list[TextRef]) -> str:
        """Apply the annottion of the specified references to the provided text.

        Parameters
        ----------
        text: str, required
            The text to annotate.

        Returns
        -------
        annotated_text: str
            The text after the annotation has been applied.
        """
        chars = [c for c in text]
        for start, end, val in reversed(references):
            chars.insert(end + 1, Marks.REFERENCE)
            chars.insert(start, Marks.REFERENCE)
        text = "".join(chars)
        return text

    def __merge_overlaps(self, references: list[TextRef]) -> list[TextRef]:
        """Merge the overlaps between adjacent references.

        Parameters
        ----------
        references: list of TextRef, required
            The references to merge.

        Returns
        -------
        merged: list of TextRef
            The list of merged references.
        """
        if len(references) < 2:
            return references

        result = []
        current_start, current_end, current_value = references[0]
        for i in range(1, len(references)):
            start, end, value = references[i]
            if start <= current_end:
                current_end = max(current_end, end)
            else:
                ref = TextRef(current_start, current_end, current_value)
                result.append(ref)
                current_start, current_end, current_value = start, end, value
        result.append(TextRef(current_start, current_end, current_value))
        return result

    def __search_references(self, text: str) -> list[TextRef]:
        """Search for references in the provided text.

        Parameters
        ----------
        text: str, required
            The text where to search for references.

        Returns
        -------
        references: list of TextRef
            The references found in text.
        """
        found_refs = []
        for end_idx, (insert_order,
                      original_value) in self.__automaton.iter(text):
            start_idx = end_idx - len(original_value) + 1
            ref = TextRef(start_idx, end_idx, original_value)
            found_refs.append(ref)
        return found_refs

    def __make_automaton(self) -> ahocorasick.Automaton:
        """Make the automaton for fast searching of references.

        Returns
        -------
        automaton: ahocorasick.Automaton
            The automaton for fast search within text.
        """
        automaton = ahocorasick.Automaton()
        if len(self.__references) > 0:
            for idx, key in enumerate(self.__references):
                key = key.strip()
                automaton.add_word(key, (idx, key))
            automaton.make_automaton()
        return automaton
