"""
This module provides the ReadWriteServiceInterface class, which defines the interface for service classes
that handle read and write operations on a model.
"""

from abc import abstractmethod
from typing import TypeVar, Type
from pydantic import BaseModel

from .read_service_interface import ReadServiceInterface
from ...repositories.base.base_repository import BaseRepository

S = TypeVar('S', bound=BaseModel)

@abstractmethod
class ReadWriteServiceInterface(ReadServiceInterface[S]):
    """
    Interface for service classes that handle read and write operations on a model.
    """

    @abstractmethod
    async def create(self, item: S) -> S:
        """
        Create a new item, ensuring it does not already exist based on unique fields.

        Args:
            item (S): The item to be created.

        Returns:
            S: The created item.
        """
        pass

    @abstractmethod
    async def update(self, item_data: S) -> S:
        """
        Update an item by its ID.

        Args:
            item_data (S): The item data to be updated.

        Returns:
            S: The updated item.
        """
        pass

    @abstractmethod
    async def delete(self, item_id: str) -> None:
        """
        Delete an item by its ID.

        Args:
            item_id (str): The ID of the item to be deleted.

        Returns:
            None
        """
        pass

