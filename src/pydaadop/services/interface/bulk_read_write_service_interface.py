from abc import abstractmethod
from typing import TypeVar, Type, List
from pydantic import BaseModel
from pymongo import UpdateMany
from pymongo.results import InsertManyResult, BulkWriteResult

from .read_service_interface import ReadServiceInterface
from .read_write_service_interface import ReadWriteServiceInterface
from ...models.base import BaseMongoModel
from ...repositories.base.base_repository import BaseRepository

S = TypeVar('S', bound=BaseMongoModel)

@abstractmethod
class BulkReadWriteServiceInterface(ReadWriteServiceInterface[S]):

    @abstractmethod
    async def create_many(self, item: [S]) -> InsertManyResult:
        """Create a new item, ensuring it does not already exist based on unique fields."""
        pass

    @abstractmethod
    async def update_many(self, items: [S]) -> BulkWriteResult:
        """Update an item by its ID."""
        pass

    @abstractmethod
    async def update_field_many(self, key_filter_queries: List[dict], data: dict) -> BulkWriteResult:
        """Update an item by its ID."""
        pass

    @abstractmethod
    async def delete_many(self, key_filter_queries: [dict]) -> None:
        """Delete an item by its ID."""
        pass

