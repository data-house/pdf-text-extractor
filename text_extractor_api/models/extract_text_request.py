from typing import List, Optional
from pydantic import BaseModel


class ExtractTextRequest(BaseModel):
    path: str
    mime_type: str
    driver: str
    unit: Optional[str] = None
    roles: Optional[List[str]] = None
