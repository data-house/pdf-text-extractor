from typing import List, Optional

from pydantic import BaseModel, Field

from text_extractor.models.node import Node


class Document(BaseModel):
    type: str = Field("doc")
    content: List[Node]
