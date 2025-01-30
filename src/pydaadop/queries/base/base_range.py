from typing import Optional, Literal

from fastapi import Query
from pydantic import BaseModel, Field

class BaseRange(BaseModel):
    range_by: Optional[str] = Query(default=None, min_length=1, max_length=100, description="Field to range by")
    gte_value: Optional[str] = Query(default=None, min_length=1, max_length=100, description="Minimum value")
    lte_value: Optional[str] = Query(default=None, min_length=1, max_length=100, description="Maximum value")

