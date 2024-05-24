from typing import List, Optional
from pydantic import BaseModel

from text_extractor_api.models import Color
from text_extractor_api.models import Font
from text_extractor_api.models import Paragraph


class Document(BaseModel):
    fonts: Optional[List[Font]] = None
    paragraphs: List[Paragraph]
    colors: Optional[List[Color]] = None
