from typing import Optional, List

from pydantic import BaseModel
from typing_extensions import TypedDict


class BoundingBox(TypedDict):
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    page: int


class Attributes(BaseModel):
    boundingBox: Optional[List[BoundingBox]] = []
