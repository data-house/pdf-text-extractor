from typing import List, Optional
from pydantic import BaseModel

from text_extractor_api.models import Position
from text_extractor_api.models import Color
from text_extractor_api.models import Font


class Paragraph(BaseModel):
    role: Optional[str] = None
    color: Optional[Color] = None
    positions: List[Position]
    text: str
    font: Optional[Font] = None
