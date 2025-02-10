from pydantic import BaseModel, Field

class DisplayItemInfo(BaseModel):
    """
    Model representing item information for display.

    Attributes:
        items_count (int): Total number of items.
    """
    items_count: int = Field(default=0, description="Total number of items")
