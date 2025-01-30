from abc import abstractmethod
from typing import TypeVar, Type
from pydantic import BaseModel

from .read_service_interface import ReadServiceInterface
from ...repositories.base.base_repository import BaseRepository

S = TypeVar('S', bound=BaseModel)

@abstractmethod
class ReadWriteServiceInterface(ReadServiceInterface[S]):

    @abstractmethod
    async def create(self, item: S) -> S:
        """Create a new item, ensuring it does not already exist based on unique fields."""
        pass

    @abstractmethod
    async def update(self, item_data: S) -> S:
        """Update an item by its ID."""
        pass

    @abstractmethod
    async def delete(self, item_id: str) -> None:
        """Delete an item by its ID."""
        pass

