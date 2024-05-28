from typing import List, Optional
from pydantic import BaseModel

from text_extractor_api.models import Position
from text_extractor_api.models import Color
from text_extractor_api.models import Font


class Metadata(BaseModel):
    role: Optional[str] = None
    color: Optional[Color] = None
    positions: Optional[List[Position]]
    font: Optional[Font] = None
    page: int


class Paragraph(BaseModel):
    text: str
    metadata: Metadata
