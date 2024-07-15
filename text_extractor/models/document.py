from typing import List, Union

from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from text_extractor.models.marks import Mark, TextStyleMark


class BoundingBox(TypedDict):
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    page: int


class Attributes(BaseModel):
    bounding_box: List[BoundingBox] = []


class Content(BaseModel):
    role: str = "body"
    text: str
    marks: List[Union[Mark, TextStyleMark]] = []
    attributes: Attributes = Attributes()


class NodeAttributes(BaseModel):
    page: int


class Node(BaseModel):
    category: str = Field("page")
    attributes: NodeAttributes
    content: List[Content]


class Document(BaseModel):
    type: str = Field("doc")
    content: List[Node]
