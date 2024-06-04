from typing import List, Optional

from pydantic import BaseModel

from text_extractor.models import Color
from text_extractor.models import Font
from text_extractor.models import Position


class Metadata(BaseModel):
    role: Optional[str] = None
    color: Optional[Color] = None
    positions: Optional[List[Position]] = None
    font: Optional[Font] = None
    page: int


class Paragraph(BaseModel):
    text: str
    metadata: Metadata
