from typing import List

import fitz

from text_extractor.models import Chunk
from parse_document_model.attributes import PageAttributes
from parse_document_model import Document, Page
from parse_document_model.document import Text
from text_extractor.parser.pdf_parser import PDFParser, clean_text


class PymupdfParser(PDFParser):
    def parse(self, filename: str, **kwargs) -> Document:
        pdf = fitz.open(filename)
        documents = []
        for page in pdf:
            text = page.get_text()
            text = clean_text(text)
            documents.append(Chunk(text, {"page_number": page.number + 1}))
        return chunks_to_document(documents)


def chunks_to_document(doc_parsed: List[Chunk]) -> Document:
    pages = []
    for page in doc_parsed:
        page_number = page.metadata['page_number']
        attributes = PageAttributes(page=page_number)
        content = [Text(content=page.text, category="body")]

        page = Page(
            attributes=attributes,
            content=content
        )

        pages.append(page)

    document = Document(
        content=pages,
    )
    return document
