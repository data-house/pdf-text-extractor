from typing import List

import fitz

from text_extractor.models import Document, Chunk, Content, NodeAttributes, Node
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
    nodes = []
    for page in doc_parsed:
        page_number = page.metadata['page_number']
        attributes = NodeAttributes(page=page_number)
        content = [Content(text=page.text)]

        node = Node(
            attributes=attributes,
            content=content
        )

        nodes.append(node)

    document = Document(
        content=nodes,
    )
    return document
