from typing import List

from pydantic import BaseModel, Field

from text_extractor.models.content import Content


class Attributes(BaseModel):
    page_number: int


class Node(BaseModel):
    type: str = Field("page")
    attributes: Attributes
    content: List[Content]
