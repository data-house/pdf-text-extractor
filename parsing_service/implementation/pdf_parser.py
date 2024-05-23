import os
import re
from typing import List
import pandas as pd
import subprocess
import json

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

    def parse_to_json(self, filename: str):
        filepath = os.path.dirname(filename)
        filename = os.path.basename(filename)
        output = os.path.splitext(filename)[0]
        command = f"docker run --rm -v {filepath}:/app/pdfs parser " \
                  f"java -jar ./pdfact.jar --format json /app/pdfs/{filename} /app/pdfs/{output}.json"

        try:
            subprocess.check_output(command, shell=True)

            output_path = f"{filepath}/{output}.json"
            if os.path.exists(output_path):
                with open(output_path, 'r') as json_file:
                    return json.load(json_file)
            else:
                raise FileNotFoundError(f"JSON file not found: {output_path}")
        except subprocess.CalledProcessError as e:
            print("Error occurred while executing the command:", e.output.decode())
            return None
