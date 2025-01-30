from typing import Optional, Literal

from fastapi import Query
from pydantic import BaseModel, Field

class BaseSelect(BaseModel):
    selected_field: Optional[str] = Query(default=None, min_length=1, max_length=100, description="Select field to return")



