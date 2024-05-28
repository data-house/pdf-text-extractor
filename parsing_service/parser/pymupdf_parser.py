import os

import pymupdf

from parsing_service.parser.pdf_parser import PDFParser, clean_text


class PymupdfParser(PDFParser):
    def parse(self, filename: str, **kwargs) -> list:
        pdf = pymupdf.open(filename)
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
        return documents