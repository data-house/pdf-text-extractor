import os
import re
from typing import List

import fitz

from parsing_service.implementation.chunk import Chunk
from parsing_service.models.chunck import AChunk
from parsing_service.models.parser import Parser


class PDFParser(Parser):

    def __init__(self):
        super().__init__()

    def parse(self, filename: str) -> List[AChunk]:
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
            # Merge hyphenated words
            text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
            # Fix newlines in the middle of sentences
            text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
            # Remove multiple newlines
            text = re.sub(r"\n\s*\n", "\n\n", text)
            text = re.sub(r'\s+', ' ', text)
            # Remove repeated special characters
            text = re.sub(r"([^\w\s])\1+", r"\1", text)
            documents.append(Chunk(text, {"page_number": page.number + 1}))

        return documents
