#!/usr/bin/env python
import argparse
from pathlib import Path
import re

CEDILLA_DIACRITICS_MAP = str.maketrans("ŞşŢţ", "ȘșȚț")


class Marks:
    """Defines the marks used annotations."""

    BOLD = '**'
    EMPHASIS = '*'
    SUPERSCRIPT = '^'
    SUBSCRIPT = '_'
    REFERENCE = '@'
    SPACED = '$'


def correct_diacritics(text: str) -> str:
    """Replace diacritics with cedilla to diacritics with comma below in te input text.

    Parameters
    ----------
    text: str, required
        The input text.

    Returns
    -------
    corrected_text: str
        The text with proper diacritics.
    """
    return text.translate(CEDILLA_DIACRITICS_MAP)


def remove_annotation_marks(text: str) -> str:
    """Remove the annotation marks from the provided text.

    Parameters
    ----------
    text: str, required
        The text from which to remove the annotation marks.

    Returns
    -------
    stripped_text: str
        The text without the annotation marks.
    """
    marks = [
        Marks.BOLD, Marks.EMPHASIS, Marks.REFERENCE, Marks.SPACED,
        Marks.SUBSCRIPT, Marks.SUPERSCRIPT
    ]
    pattern = re.compile('|'.join(map(re.escape, marks)))
    return pattern.sub('', text)


def convert_xml_to_edtlr_markdown(xml_string: str) -> str:
    """Conver the provided XML string to eDTLR markdown.

    Parameters
    ----------
    xml_string: str, required
        The XML string to convert.

    Returns
    -------
    markdown_string: str
        The input string converted to eDTLR markdown.
    """
    data = xml_string.strip()
    data = re.sub(r"<\/?entry>", "", data)
    data = re.sub(r"<\/?p>", "\n", data)
    data = re.sub(r"<\/?b>", Marks.BOLD, data)
    data = re.sub(r"<\/?i>", Marks.EMPHASIS, data)
    data = re.sub(r"<\/?sup>", Marks.SUPERSCRIPT, data)
    data = re.sub(r"<\/?sg>", Marks.REFERENCE, data)
    return correct_diacritics(data.strip())


def main(input_file: Path, output_file: Path = None):
    """Do the logic."""
    if output_file is None:
        output_file = Path(f'{input_file.stem}.md')

    with open(input_file, encoding='utf8') as f:
        input_string = f.read()

    input_string = convert_xml_to_edtlr_markdown(input_string)

    with open(output_file, mode="w", encoding='utf8') as f:
        f.write(input_string)


def parse_arguments():
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser(description='xml2edtlrmd')
    parser.add_argument('--input-file',
                        required=True,
                        help="The path of the input XML file.")
    parser.add_argument('--output-file',
                        required=False,
                        help="The path of the output file.")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    main(Path(args.input_file),
         Path(args.output_file) if args.output_file is not None else None)
