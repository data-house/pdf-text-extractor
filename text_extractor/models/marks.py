from pydantic import BaseModel, model_validator
from typing import Literal, Optional
from typing import Any

from text_extractor.models.color import Color
from text_extractor.models.font import Font


class Mark(BaseModel):
    category: Literal['bold', 'italic', 'textStyle', 'link']

    @model_validator(mode='before')
    @classmethod
    def check_details(cls, data: Any) -> Any:
        mark_type = data.get('type')

        if mark_type == 'textStyle':
            if 'color' not in data and 'font' not in data:
                raise ValueError('color or font must be provided when type is textStyle')
            if 'url' in data:
                raise ValueError('url should not be provided when type is textStyle')

        elif mark_type == 'link':
            if 'url' not in data:
                raise ValueError('url must be provided when type is link')
            if 'textStyle' in data:
                raise ValueError('textStyle should not be provided when type is link')

        return data


class TextStyleMark(Mark):
    color: Optional[Color] = None
    font: Optional[Font] = None


class UrlMark(Mark):
    url: str
