from typing import Optional, Literal

from fastapi import Query
from pydantic import BaseModel, Field

class BaseSort(BaseModel):
    """
    BaseSort class for sorting query results.

    Attributes:
        sort_by (Optional[str]): Field to sort by.
        sort_order (Literal["asc", "desc"]): Sort order: 'asc' for ascending, 'desc' for descending.
    """
    sort_by: Optional[str] = Query(default=None, min_length=1, max_length=100, description="Field to sort by")
    sort_order: Literal["asc", "desc"] = Query(default="asc", description="Sort order: 'asc' for ascending, 'desc' for descending")

