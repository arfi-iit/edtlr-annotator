#!/usr/bin/env python
import argparse
from pathlib import Path
import re

CEDILLA_DIACRITICS_MAP = str.maketrans("ŞşŢţ", "ȘșȚț")


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
    data = re.sub(r"<\/?b>", "**", data)
    data = re.sub(r"<\/?i>", "*", data)
    data = re.sub(r"<\/?sup>", "^", data)
    data = re.sub(r"<\/?sg>", "@", data)
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
