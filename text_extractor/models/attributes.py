from typing import Optional, List

from pydantic import BaseModel


class BoundingBox(BaseModel):
    minY: float
    minX: float
    maxY: float
    maxX: float
    page: int


class Attributes(BaseModel):
    boundingBox: Optional[List[BoundingBox]] = []
