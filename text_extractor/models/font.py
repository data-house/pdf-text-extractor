from typing import Optional

from pydantic import BaseModel, Field


class Font(BaseModel):
    name: str
    id: str
    size: Optional[int] = None
