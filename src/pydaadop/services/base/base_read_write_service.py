"""
This module provides the BaseReadWriteService class, which implements the ReadWriteServiceInterface
and provides methods for creating, updating, and deleting items in a MongoDB collection.
"""

from abc import ABC
from typing import TypeVar, Type
from fastapi import HTTPException
from pydantic import BaseModel
from typing_extensions import override

from .base_read_service import BaseReadService
from ..interface.read_write_service_interface import ReadWriteServiceInterface
from ...models.base import BaseMongoModel
from ...repositories.base.base_read_write_repository import BaseReadWriteRepository

S = TypeVar('S', bound=BaseMongoModel)
R = TypeVar('R', bound=BaseReadWriteRepository[BaseMongoModel])

class BaseReadWriteService(ReadWriteServiceInterface[S], BaseReadService[S], ABC):
    """
    Service class for handling read and write operations on a MongoDB collection.

    Attributes:
        model (Type[S]): The model class.
        repository (R): The repository instance for database operations.
    """

    def __init__(self, model: Type[S], repository: R = None):
        """
        Initialize the BaseReadWriteService.

        Args:
            model (Type[S]): The model class.
            repository (R, optional): The repository instance for database operations. Defaults to None.
        """
        self.repository = repository if repository else BaseReadWriteRepository(model)
        super().__init__(model, self.repository)

    @override
    async def create(self, item: S) -> S:
        """
        Create a new item, ensuring it does not already exist based on unique fields.

        Args:
            item (S): The item to be created.

        Returns:
            S: The created item.

        Raises:
            HTTPException: If the item already exists.
        """
        existing_item = await self.repository.exists(item.model_dump_keys())
        if existing_item:
            raise HTTPException(status_code=400, detail="Item already exists.")
        return await self.repository.create(item)

    @override
    async def update(self, item: S) -> S:
        """
        Update an item by its ID.

        Args:
            item (S): The item data to be updated.

        Returns:
            S: The updated item.

        Raises:
            HTTPException: If the item does not exist.
        """
        exists = await self.repository.exists(item.model_dump_keys())
        if not exists: # create the item
            return await self.create(item)
        return await self.repository.update(item.model_dump_keys(), item)

    @override
    async def delete(self, keys_filter_query: dict) -> None:
        """
        Delete an item by its ID.

        Args:
            keys_filter_query (dict): The filter query to identify the item.

        Returns:
            None

        Raises:
            HTTPException: If the item is not found.
        """
        existing_item = await self.repository.get_by_id(keys_filter_query)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Item not found.")
        await self.repository.delete(keys_filter_query)
