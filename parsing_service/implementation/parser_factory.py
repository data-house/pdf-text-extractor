from typing import List

from parsing_service.implementation.pdf_parser import PDFParser
from parsing_service.models.chunck import AChunk


def parse_file(filename: str, filetype: str) -> List[AChunk]:
    """
    Parse the given file and return a list of chunks.
    :param filename: The name of the file to parse.
    :param filetype: The type of the file to parse.
    :return: A list of extracted chunks.
    """
    if filetype != "pdf":
        raise ValueError(f"Invalid filetype {filetype}")

    parser = PDFParser()
    context = parser.pdfAct(filename)
    return context

