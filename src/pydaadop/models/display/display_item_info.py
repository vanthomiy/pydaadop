from pydantic import BaseModel, Field

class DisplayItemInfo(BaseModel):
    items_count: int = Field(default=0, description="Total number of items")
