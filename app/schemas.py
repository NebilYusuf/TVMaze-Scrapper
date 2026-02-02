from typing import List, Optional
from pydantic import BaseModel, Field

class CastOut(BaseModel):
    id: int
    name: str
    birthday: Optional[str] = None

class ShowOut(BaseModel):
    id: int
    name: str
    cast: List[CastOut] = Field(default_factory=list)

class PaginatedShows(BaseModel):
    page: int
    page_size: int
    total: int
    items: List[ShowOut]
