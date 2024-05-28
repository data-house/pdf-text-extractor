import requests

from parsing_service.parser.pdf_parser import PDFParser
from parsing_service.parser.parser_utils import convert_json_to_document
from parsing_service.models import Document


class PdfactParser(PDFParser):

    def parse(self, filename: str, **kwargs) -> Document:
        url = "http://127.0.0.1:4567/api/pdf/parse"
        body = {"url": filename}
        unit = kwargs.get("unit", None)
        roles = kwargs.get("roles", None)
        if unit is not None:
            body["unit"] = unit
        if roles is not None:
            body["roles"] = roles
        response = requests.post(url, json=body)
        response.raise_for_status()
        res = response.json()
        if unit == 'paragraph' or unit is None:
            res = pdfact_formatter(res)
        document = convert_json_to_document(res)
        return document


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
