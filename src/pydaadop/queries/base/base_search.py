from typing import Optional, Literal

from fastapi import Query
from pydantic import BaseModel, Field

class BaseSearch(BaseModel):
    search: Optional[str] = Query(None, description="Search string")
