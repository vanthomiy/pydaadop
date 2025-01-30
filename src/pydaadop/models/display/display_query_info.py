from typing import List, Optional
from pydantic import BaseModel, Field

class DisplayFilterAttributeInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the filter attribute")
    type: Optional[str] = Field(default=None, description="Data type of the filter attribute")
    allowed_values: Optional[List[str]] = Field(default=None, description="List of allowed values for the filter attribute")
    parent: Optional[str] = Field(default=None, description="Parent filter attribute")

class DisplaySortAttributeInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the filter attribute")
    parent: Optional[str] = Field(default=None, description="Parent filter attribute")

class DisplayFilterInfo(BaseModel):
    filter_attributes: List[DisplayFilterAttributeInfo] = Field(default_factory=list, description="List of filter attributes")

class DisplaySortInfo(BaseModel):
    sort_attributes: List[DisplaySortAttributeInfo] = Field(default_factory=list, description="List of sort attributes")

class DisplayQueryInfo(BaseModel):
    filter_info: Optional[DisplayFilterInfo] = Field(default=None, description="Filter information for the items")
    sort_info: Optional[DisplaySortInfo] = Field(default=None, description="Sort information for the items")
