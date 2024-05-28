import os
from parsing_service.models.chunk import Chunk

import fitz

from parsing_service.parser.pdf_parser import PDFParser, clean_text
from parsing_service.parser.parser_utils import convert_to_document
from parsing_service.models import Document


class PymupdfParser(PDFParser):
    def parse(self, filename: str, **kwargs) -> Document:
        pdf = fitz.open(filename)
        documents = []
        skipping = False
        for page in pdf:
            text = page.get_text()
            if os.environ.get("REMOVE_METHODOLOGY_CHAPTER", "True").lower() == "true":
                if text.startswith("2 EVALUIERUNGSDESIGN UND METHODOLOGIE"):
                    skipping = True
                if text.startswith("3 ERGEBNISSE DER EVALUIERUNG"):
                    skipping = False
            if skipping:
                continue
            text = clean_text(text)
            documents.append(Chunk(text, {"page_number": page.number + 1}))
            doc_parsed = {"status": "ok", "content": [chunk.to_dict() for chunk in documents]}
            document = convert_to_document(doc_parsed)
        return document
