from fastapi import Query
from pydantic import BaseModel, Field


class BasePaging(BaseModel):
    page: int = Query(default=1, ge=1, description="The page number to retrieve (must be greater than or equal to 1)")
    page_size: int = Query(default=10, ge=1, le=100000, description="The number of items per page (must be between 1 and 100)")


    def skip(self):
        return (self.page - 1) * self.page_size

    def limit(self):
        return self.page_size


