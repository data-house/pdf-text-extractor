from text_extractor_api.models import Color, Font, Position, Paragraph, Document


def convert_json_to_document(json_data: dict) -> Document:
    colors = [Color(**color) for color in json_data.get('colors', [])]

    fonts = [Font(**font) for font in json_data.get('fonts', [])]

    paragraphs = []
    for para in json_data.get('paragraphs', []):
        paragraph_detail = para['paragraph']
        color_id = paragraph_detail['color']['id']

        color = next((c for c in colors if c.id == color_id), None)

        font_id = paragraph_detail['font']['id']
        font = next((f for f in fonts if f.id == font_id), None)

        positions = [Position(**pos) for pos in paragraph_detail.get('positions', [])]

        paragraph = Paragraph(
            role=paragraph_detail['role'],
            color=color,
            positions=positions,
            text=paragraph_detail['text'],
            font=font
        )

        paragraphs.append(paragraph)

    document = Document(
        fonts=fonts,
        paragraphs=paragraphs,
        colors=colors
    )

    return document


def convert_to_document(doc_parsed) -> Document:
    paragraphs = []
    for page in doc_parsed.get('content', []):
        page_number = page['metadata']['page_number']

        position = Position(page=page_number)

        paragraph = Paragraph(
            positions=[position],
            text=page['text']
        )

        paragraphs.append(paragraph)

    document = Document(
        paragraphs=paragraphs,
    )
    return document

