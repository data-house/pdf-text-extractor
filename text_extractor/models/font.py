from pydantic import BaseModel, Field


class Font(BaseModel):
    name: str
    id: str
    is_bold: bool = Field(False, alias='is-bold')
    is_type3: bool = Field(False, alias='is-type3')
    is_italic: bool = Field(False, alias='is-italic')
