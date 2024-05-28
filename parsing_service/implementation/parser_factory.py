from typing import List
import json

from parsing_service.implementation.pdf_parser import PDFParser
from parsing_service.models.chunk import AChunk
from parsing_service.implementation.utils import pdfact_formatter as json_formatter


def parse_file(filename: str) -> List[AChunk]:
    """
    Parse the given file and return a list of chunks.
    :param filename: The name of the file to parse.
    :return: A list of extracted chunks.
    """
    parser = PDFParser()
    context = parser.parse(filename)
    return context


def parse_file_to_json(filename: str, unit: str = None, roles: list = None):
    """
    Parses the given file and returns the data as JSON.
    :param filename: The name of the file to parse.
    :param unit:
    :param roles:
    :return: The parsed data in JSON format.
    """
    parser = PDFParser()
    context = parser.parse_to_json(filename, unit, roles)
    if unit == 'paragraph' or unit is None:
        file_json = json_formatter(context)
    else:
        file_string = json.dumps(context, indent=2)
        file_json = json.loads(file_string)
    return file_json


