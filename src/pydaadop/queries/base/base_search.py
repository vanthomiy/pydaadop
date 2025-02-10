from typing import Optional, Literal

from fastapi import Query
from pydantic import BaseModel, Field

class BaseSearch(BaseModel):
    """
    BaseSearch class for searching query results.

    Attributes:
        search (Optional[str]): Search string.
    """
    search: Optional[str] = Query(None, description="Search string")
