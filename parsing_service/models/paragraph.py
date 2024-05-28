from typing import List, Optional
from pydantic import BaseModel

from parsing_service.models import Position
from parsing_service.models import Color
from parsing_service.models import Font


class Metadata(BaseModel):
    role: Optional[str] = None
    color: Optional[Color] = None
    positions: Optional[List[Position]] = None
    font: Optional[Font] = None
    page: int


class Paragraph(BaseModel):
    text: str
    metadata: Metadata
