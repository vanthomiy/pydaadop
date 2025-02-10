"""
This module provides the BaseReadWriteRepository class, which implements the repository
for reading and writing MongoDB models.

Classes:
    BaseReadWriteRepository: A repository class for reading and writing MongoDB models.
"""

from typing import Type, TypeVar, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from .base_read_repository import BaseReadRepository
from ...models.base import BaseMongoModel

T = TypeVar("T", bound=BaseMongoModel)

class BaseReadWriteRepository(BaseReadRepository[T]):
    """
    A repository class for reading and writing MongoDB models.

    Attributes:
        collection (AsyncIOMotorCollection): The MongoDB collection.
    """

    def __init__(self, model: Type[T], collection: AsyncIOMotorCollection = None):
        """
        Initialize the BaseReadWriteRepository.

        Args:
            model (Type[T]): The MongoDB model type.
            collection (AsyncIOMotorCollection, optional): The MongoDB collection. Defaults to None.
        """
        super().__init__(model, collection)

    async def create(self, item: T) -> T:
        """
        Create an item.

        Args:
            item (T): The item to create.

        Returns:
            T: The created item.
        """
        result = await self.collection.insert_one(item.model_dump())
        item.id = str(result.inserted_id)  # Ensure the model has an 'id' field
        return item

    async def update(self, keys_filter_query: dict, item_data: T) -> Optional[T]:
        """
        Update an item.

        Args:
            keys_filter_query (dict): The key filter query.
            item_data (T): The item data to update.

        Returns:
            Optional[T]: The updated item, or None if not found.
        """
        await self.collection.update_one(keys_filter_query, {"$set": item_data.model_dump(ignore_id=True)})
        return await self.get_by_id(keys_filter_query)

    async def delete(self, keys_filter_query: dict) -> None:
        """
        Delete an item.

        Args:
            keys_filter_query (dict): The key filter query.
        """
        await self.collection.delete_one(keys_filter_query)
