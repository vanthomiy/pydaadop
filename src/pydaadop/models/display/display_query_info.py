from typing import List, Optional
from pydantic import BaseModel, Field

class DisplayFilterAttributeInfo(BaseModel):
    """
    Model representing a filter attribute for display.

    Attributes:
        name (Optional[str]): Name of the filter attribute.
        type (Optional[str]): Data type of the filter attribute.
        allowed_values (Optional[List[str]]): List of allowed values for the filter attribute.
        parent (Optional[str]): Parent filter attribute.
    """
    name: Optional[str] = Field(default=None, description="Name of the filter attribute")
    type: Optional[str] = Field(default=None, description="Data type of the filter attribute")
    allowed_values: Optional[List[str]] = Field(default=None, description="List of allowed values for the filter attribute")
    parent: Optional[str] = Field(default=None, description="Parent filter attribute")

class DisplaySortAttributeInfo(BaseModel):
    """
    Model representing a sort attribute for display.

    Attributes:
        name (Optional[str]): Name of the sort attribute.
        parent (Optional[str]): Parent sort attribute.
    """
    name: Optional[str] = Field(default=None, description="Name of the filter attribute")
    parent: Optional[str] = Field(default=None, description="Parent filter attribute")

class DisplayFilterInfo(BaseModel):
    """
    Model representing filter information for display.

    Attributes:
        filter_attributes (List[DisplayFilterAttributeInfo]): List of filter attributes.
    """
    filter_attributes: List[DisplayFilterAttributeInfo] = Field(default_factory=list, description="List of filter attributes")

class DisplaySortInfo(BaseModel):
    """
    Model representing sort information for display.

    Attributes:
        sort_attributes (List[DisplaySortAttributeInfo]): List of sort attributes.
    """
    sort_attributes: List[DisplaySortAttributeInfo] = Field(default_factory=list, description="List of sort attributes")

class DisplayQueryInfo(BaseModel):
    """
    Model representing query information for display.

    Attributes:
        filter_info (Optional[DisplayFilterInfo]): Filter information for the items.
        sort_info (Optional[DisplaySortInfo]): Sort information for the items.
    """
    filter_info: Optional[DisplayFilterInfo] = Field(default=None, description="Filter information for the items")
    sort_info: Optional[DisplaySortInfo] = Field(default=None, description="Sort information for the items")
