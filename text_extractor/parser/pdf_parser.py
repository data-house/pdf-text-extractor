import re
from abc import ABC, abstractmethod

from parse_document_model import Document


class PDFParser(ABC):
    @abstractmethod
    def parse(self, filename: str, **kwargs) -> Document:
        pass


def clean_text(text: str) -> str:
    # Merge hyphenated words
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    # Fix newlines in the middle of sentences
    text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    # Replace multiple whitespaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove repeated special characters
    text = re.sub(r"([^\w\s])\1+", r"\1", text)
    return text
