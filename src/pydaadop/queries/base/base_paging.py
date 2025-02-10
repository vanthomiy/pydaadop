from fastapi import Query
from pydantic import BaseModel, Field

class BasePaging(BaseModel):
    """
    BasePaging class for pagination in query results.

    Attributes:
        page (int): The page number to retrieve (must be greater than or equal to 1).
        page_size (int): The number of items per page (must be between 1 and 100).
    """
    page: int = Query(default=1, ge=1, description="The page number to retrieve (must be greater than or equal to 1)")
    page_size: int = Query(default=10, ge=1, le=100000, description="The number of items per page (must be between 1 and 100)")

    def skip(self):
        """
        Calculate the number of items to skip based on the current page and page size.

        Returns:
            int: The number of items to skip.
        """
        return (self.page - 1) * self.page_size

    def limit(self):
        """
        Get the limit of items per page.

        Returns:
            int: The number of items per page.
        """
        return self.page_size


