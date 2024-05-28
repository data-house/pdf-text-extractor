from parsing_service.models import Color, Font, Position, Metadata, Paragraph, Document


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

        positions = [
            Position(
                minY=pos['minY'],
                minX=pos['minX'],
                maxY=pos['maxY'],
                maxX=pos['maxX']
            ) for pos in paragraph_detail.get('positions', [])
        ]

        page = paragraph_detail['positions'][0]['page'] if paragraph_detail.get('positions') else None

        metadata = Metadata(
            role=paragraph_detail['role'],
            color=color,
            positions=positions,
            font=font,
            page=page
        )
        paragraph = Paragraph(
            text=paragraph_detail['text'],
            metadata=metadata
        )

        paragraphs.append(paragraph)

    document = Document(
        fonts=fonts,
        text=paragraphs,
        colors=colors
    )

    return document


def convert_to_document(doc_parsed: dict) -> Document:
    paragraphs = []
    for page in doc_parsed.get('content', []):
        page_number = page['metadata']['page_number']

        metadata = Metadata(page=page_number)

        paragraph = Paragraph(
            text=page['text'],
            metadata=metadata
        )

        paragraphs.append(paragraph)

    document = Document(
        text=paragraphs,
    )
    return document
