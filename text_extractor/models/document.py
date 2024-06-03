from typing import List, Optional
from pydantic import BaseModel

from parsing_service.models import Color
from parsing_service.models import Font
from parsing_service.models import Paragraph


class Document(BaseModel):
    fonts: Optional[List[Font]] = None
    text: List[Paragraph]
    colors: Optional[List[Color]] = None
