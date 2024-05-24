from pydantic import BaseModel


class Color(BaseModel):
    r: int
    b: int
    g: int
    id: str
