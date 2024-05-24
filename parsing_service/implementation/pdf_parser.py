import os
import re
from typing import List
import requests

import fitz

from parsing_service.implementation.chunk import Chunk
from parsing_service.models.chunck import AChunk
from parsing_service.models.parser import Parser


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
            text = clean_text(text)
            documents.append(Chunk(text, {"page_number": page.number + 1}))
        return documents

    def parse_to_json(self, filename: str, unit: str = None, roles: str = None):
        url = "http://127.0.0.1:4567/api/pdf/parse"
        body = {
            "url": filename
        }

        if unit is not None:
            body["unit"] = unit

        if roles is not None:
            if isinstance(roles, list) and all(isinstance(role, str) for role in roles):
                body["roles"] = roles
            else:
                print("Error: roles is not a list of string")
                return None

        try:

            response = requests.post(url, json=body)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Errore nella richiesta: {e}")
            return None


