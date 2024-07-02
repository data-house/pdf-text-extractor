from typing import List, Optional, Union

from pydantic import BaseModel

from text_extractor.models.attributes import Attributes
from text_extractor.models.marks import Mark, TextStyleMark


class Content(BaseModel):
    type: Optional[str] = "body"
    text: str
    marks: Optional[List[Union[Mark, TextStyleMark]]] = []
    attributes: Optional[Attributes] = []
