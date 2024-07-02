import logging

import requests
from fastapi import HTTPException
from requests.exceptions import RequestException

from text_extractor.models import Document, Color, Font
from text_extractor.models.marks import Mark, TextStyleMark
from text_extractor.models.content import Content
from text_extractor.models.node import Node
from text_extractor.models.node import Attributes as AttributesPage
from typing import List, Dict
from text_extractor.models.attributes import Attributes, BoundingBox
from text_extractor.parser.pdf_parser import PDFParser

logger = logging.getLogger(__name__)


class PdfactParser(PDFParser):
    def __init__(self, url: str) -> None:
        self.url = url

    def parse(self, filename: str, **kwargs) -> Document:
        body = {"url": filename}
        unit = kwargs.get("unit", None)
        roles = kwargs.get("roles", None)
        if unit is not None:
            body["unit"] = unit
        if roles is not None:
            body["roles"] = roles
        try:
            response = requests.post(self.url, json=body)
            response.raise_for_status()
            res = response.json()
            if unit == 'paragraph' or unit is None:
                res = pdfact_formatter(res)
            document = pdfact_to_document(res)
            return document
        except RequestException as e:
            logger.exception(f"An error occurred while trying to reach the API: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail="Error while trying to reach the API")


def pdfact_to_document(json_data: dict) -> Document:
    colors = [Color(**color) for color in json_data.get('colors', [])]
    fonts = [Font(**font) for font in json_data.get('fonts', [])]
    pages: Dict[int, List[Content]] = {}

    for para in json_data.get('paragraphs', []):
        paragraph_detail = para['paragraph']
        page = paragraph_detail['positions'][0]['page'] if paragraph_detail.get('positions') else None
        color_id = paragraph_detail['color']['id']
        color = next((c for c in colors if c.id == color_id), None)

        font_id = paragraph_detail['font']['id']
        font_size = paragraph_detail['font']['font-size']
        font = next((f for f in fonts if f.id == font_id), None)
        if font_size and font:
            font.size = font_size
        font_info = next((font for font in json_data.get('fonts', []) if font.get('id') == font_id), None)

        is_bold = False
        is_italic = False
        if font_info:
            is_bold = font_info.get('is-bold')
            is_italic = font_info.get('is-italic')

        # TODO implement logic for links
        marks = []
        if color or font:
            mark = TextStyleMark(type='textStyle', color=color, font=font)
            marks.append(mark)
        if is_bold:
            mark = Mark(type='bold')
            marks.append(mark)
        if is_italic:
            mark = Mark(type='italic')
            marks.append(mark)

        boundingBoxs = [
            BoundingBox(
                min_x=pos['minX'],
                min_y=pos['minY'],
                max_x=pos['maxX'],
                max_y=pos['maxY'],
                page=pos['page']
            ) for pos in paragraph_detail.get('positions', [])
        ]

        attributes = Attributes(boundingBox=boundingBoxs)

        content = Content(
            type=paragraph_detail['role'],
            text=paragraph_detail['text'],
            marks=marks,
            attributes=attributes
        )

        if page not in pages:
            pages[page] = []
        pages[page].append(content)

    nodes = [
        Node(
            attributes=AttributesPage(page_number=page, boundingBox=[]),
            content=content_list
        ) for page, content_list in pages.items()
    ]

    doc = Document(
        content=nodes
    )

    return doc


def pdfact_formatter(json_file):
    previous_length = None
    current_json = json_file
    current_length = len(current_json["paragraphs"])

    while previous_length is None or previous_length != current_length:
        previous_length = current_length
        current_json = aggregate_paragraphs(current_json)
        current_length = len(current_json["paragraphs"])

    return current_json


def aggregate_paragraphs(json_file):
    output = []
    fonts = json_file["fonts"]
    colors = json_file["colors"]
    i = 0
    while i < len(json_file["paragraphs"][:-1]):
        paragraph1 = json_file["paragraphs"][i]
        paragraph2 = json_file["paragraphs"][i + 1]

        if compare_paragraphs(paragraph1, paragraph2):
            paragraph = merge_pargraphs(paragraph1, paragraph2)
            output.append(paragraph)

            # After merging the two paragraphs, proceed to the paragraph following the (i+1)-th one
            if i + 2 < len(json_file["paragraphs"][:-1]):
                i += 2
                continue
            # if the paragraph following the (i+1)-th one is the last one, then concatenate it
            elif i + 2 == len(json_file["paragraphs"][:-1]):
                output.append(json_file["paragraphs"][i + 2])
                break
        else:
            output.append(json_file["paragraphs"][i])

            # If the next paragraph is the last one, then concatenate it to the list of paragraphs
            if i + 1 == len(json_file["paragraphs"][:-1]):
                output.append(json_file["paragraphs"][i + 1])
        i += 1

    paragraphs = {'fonts': fonts, 'paragraphs': output, 'colors': colors}
    return paragraphs


def compare_paragraphs(p1, p2, tr=25):
    if p1["paragraph"]["role"] != p2["paragraph"]["role"]:
        return False
    if p1["paragraph"]["color"] != p2["paragraph"]["color"]:
        return False
    if p1["paragraph"]["font"] != p2["paragraph"]["font"]:
        return False

    positions1, positions2 = p1["paragraph"]["positions"], p2["paragraph"]["positions"]

    for pos1 in positions1:
        for pos2 in positions2:
            # Compare if they are aligned with respect to the x-axis and if their distance is less than a threshold
            if (pos1["minX"] - pos2["minX"] == 0
                or pos1["maxX"] - pos2["maxX"] == 0
                or (pos1["minX"] + pos1["maxX"]) / 2 == (pos2["minX"] + pos2["maxX"]) / 2) \
                    and (pos1["minY"] - pos2["maxY"] < tr):
                return True
            # Compare if they are aligned with respect to the y-axis and if their distance is less than a threshold
            elif (pos1["minY"] - pos2["minY"] == 0
                  or pos1["maxY"] - pos2["maxY"] == 0
                  or (pos1["minY"] + pos1["maxY"]) / 2 == (pos2["minY"] + pos2["maxY"]) / 2) \
                    and (pos2["minX"] - pos1["maxX"] < tr):
                return True

    return False


def merge_pargraphs(p1, p2):
    role = p1["paragraph"]["role"]
    color = p1["paragraph"]["color"]
    font = p1["paragraph"]["font"]
    positions1 = p1["paragraph"]["positions"]
    positions2 = p2["paragraph"]["positions"]
    text1 = p1["paragraph"]["text"]
    text2 = p2["paragraph"]["text"]

    paragraph = {
        "paragraph": {
            "role": role,
            "color": color,
            "positions": positions1 + positions2,
            "text": text1 + '\n\n' + text2,
            "font": font
        }
    }

    return paragraph

