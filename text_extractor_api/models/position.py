from typing import Optional
from pydantic import BaseModel


class Position(BaseModel):
    minY: Optional[float] = None
    minX: Optional[float] = None
    maxY: Optional[float] = None
    maxX: Optional[float] = None
    page: int
