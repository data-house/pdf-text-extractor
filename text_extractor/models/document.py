from typing import List, Optional

from pydantic import BaseModel

from text_extractor.models.color import Color
from text_extractor.models.font import Font
from text_extractor.models.paragraph import Paragraph


class Document(BaseModel):
    fonts: Optional[List[Font]] = None
    text: List[Paragraph]
    colors: Optional[List[Color]] = None
