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
        for page in pdf:
            text = page.get_text()
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
