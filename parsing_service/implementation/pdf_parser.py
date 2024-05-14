import os
import re
from typing import List
import pandas as pd
import subprocess
import json

import fitz
from pypdf import PdfReader
from PyPDF2 import PdfReader as pdf2
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import tabula

import pdfplumber
from py_pdf_parser.loaders import load_file
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

    # PyPDF
    def parsePyPDF(self, filename: str) -> List[AChunk]:
        pdf = PdfReader(filename)
        documents = []
        skipping = False
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            if os.environ.get("REMOVE_METHODOLOGY_CHAPTER", "True").lower() == "true":
                if text.startswith("2 EVALUIERUNGSDESIGN UND METHODOLOGIE"):
                    skipping = True
                if text.startswith("3 ERGEBNISSE DER EVALUIERUNG"):
                    skipping = False
            if skipping:
                continue
            text = clean_text(text)
            documents.append(Chunk(text, {"page_number": page.page_number + 1}))
        return documents

    # PDF Parser, problemi non estrae propio il testo
    def parsePDFParser(self, filename: str) -> List[AChunk]:
        pdf = load_file(filename)
        documents = []
        skipping = False
        for page in pdf.pages:
            text = page.document.elements
            if os.environ.get("REMOVE_METHODOLOGY_CHAPTER", "True").lower() == "true":
                if text.startswith("2 EVALUIERUNGSDESIGN UND METHODOLOGIE"):
                    skipping = True
                if text.startswith("3 ERGEBNISSE DER EVALUIERUNG"):
                    skipping = False
            if skipping:
                continue
            text = clean_text(text)
            documents.append(Chunk(text, {"page_number": page.page_number}))
        return documents

    # PyPDF2
    def parsePyPDF2(self, filename: str) -> List[AChunk]:
        pdf = pdf2(filename)
        documents = []
        skipping = False
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            if os.environ.get("REMOVE_METHODOLOGY_CHAPTER", "True").lower() == "true":
                if text.startswith("2 EVALUIERUNGSDESIGN UND METHODOLOGIE"):
                    skipping = True
                if text.startswith("3 ERGEBNISSE DER EVALUIERUNG"):
                    skipping = False
            if skipping:
                continue
            text = clean_text(text)
            documents.append(Chunk(text, {"page_number": i + 1}))
        return documents

    # pdfminer.six
    def parsePdfMiner(self, filename: str) -> List[AChunk]:
        documents = []
        skipping = False
        for page_layout in extract_pages(filename):
            page_text = ""
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    page_text += element.get_text()

            page_text = clean_text(page_text)

            if os.environ.get("REMOVE_METHODOLOGY_CHAPTER", "True").lower() == "true":
                if page_text.startswith("2 EVALUIERUNGSDESIGN UND METHODOLOGIE"):
                    skipping = True
                elif page_text.startswith("3 ERGEBNISSE DER EVALUIERUNG"):
                    skipping = False
                if skipping:
                    continue

            documents.append(Chunk(page_text, {"page_number": page_layout.pageid}))
        return documents

    # PDF Plumber
    def parsePdfPlumber(self, filename: str) -> List[AChunk]:
        documents = []
        skipping = False
        with pdfplumber.open(filename) as pdf:
            for i in range(len(pdf.pages)):
                page = pdf.pages[i]
                text = page.extract_text()
                if os.environ.get("REMOVE_METHODOLOGY_CHAPTER", "True").lower() == "true":
                    if text.startswith("2 EVALUIERUNGSDESIGN UND METHODOLOGIE"):
                        skipping = True
                    if text.startswith("3 ERGEBNISSE DER EVALUIERUNG"):
                        skipping = False
                if skipping:
                    continue
                text = clean_text(text)
                documents.append(Chunk(text, {"page_number": page.page_number}))
        return documents

    def pyTabula(self, filename: str) -> pd.Series:
        dfs = tabula.read_pdf(filename, pages='all')
        series_data = pd.Series(dfs)
        return series_data

    def pdfAct(self, filename: str):
        output = os.path.splitext(filename)[0]
        command = f"docker run --rm -v /Users/annamarika/PycharmProjects/text-extractor/samples:/app/pdfs parser " \
                  f"java -jar ./pdfact.jar --format json /app/pdfs/{filename} /app/pdfs/{output}.json"

        try:
            subprocess.check_output(command, shell=True)

            output_path = f"/Users/annamarika/PycharmProjects/text-extractor/samples/{output}.json"
            if os.path.exists(output_path):
                return output_path
            else:
                raise FileNotFoundError(f"File JSON non trovato: {output_path}")
        except subprocess.CalledProcessError as e:
            print("Errore durante l'esecuzione del comando:", e.output.decode())
            return None





