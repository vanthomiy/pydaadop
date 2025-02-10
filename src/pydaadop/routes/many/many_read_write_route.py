"""
This module provides the ManyReadWriteRouter class, which sets up routes for
reading and writing multiple MongoDB models.

Classes:
    ManyReadWriteRouter: A router class for reading and writing multiple MongoDB models.
"""

from typing import Type, TypeVar, List
from fastapi import HTTPException, Depends

from ...models.base import BaseMongoModel
from ...queries.base.base_query import BaseQuery
from ...services.many.many_read_write_service import ManyReadWriteService
from ...services.interface.many_read_write_service_interface import ManyReadWriteServiceInterface
from pydantic import BaseModel
from typing_extensions import override

from ..base.base_read_write_route import BaseReadWriteRouter

T = TypeVar("T", bound=BaseMongoModel)  # Generic type for the model class

class ManyReadWriteRouter(BaseReadWriteRouter[T]):
    """
    A router class for reading and writing multiple MongoDB models.

    Attributes:
        name (str): The name of the router.
        service (ManyReadWriteServiceInterface): The service for reading and writing operations.
    """

    def __init__(self, model: Type[T], service: ManyReadWriteServiceInterface = None):
        """
        Initialize the ManyReadWriteRouter.

        Args:
            model (Type[T]): The MongoDB model type.
            service (ManyReadWriteServiceInterface, optional): The service for reading and writing operations. Defaults to None.
        """
        self.name = "many"
        self.service = service if service else ManyReadWriteService(model)
        super().__init__(model, self.service)

    @override
    def setup_routes(self):
        """
        Set up the routes for reading and writing multiple MongoDB models.
        """
        super().setup_routes()
        key_filter_model = self.service.create_key_filter()
        model = self.model  # Store the model locally for static use

        @self.router.post(f"{self.prefix}-insert-many")
        async def create_many(items: List[model]) -> dict:
            """
            Create multiple items.

            Args:
                items (List[model]): The list of items to create.

            Returns:
                dict: The IDs of the created items.
            """
            created_item = await self.service.create_many(items)
            return {"ids": created_item.inserted_ids}

        @self.router.put(f"{self.prefix}-update-many")
        async def update_many(items: List[model]) -> dict:
            """
            Update multiple items.

            Args:
                items (List[model]): The list of items to update.

            Returns:
                dict: The count of updated items.

            Raises:
                HTTPException: If no items are updated.
            """
            updated_item = await self.service.update_many(items)
            if not updated_item:
                raise HTTPException(status_code=404, detail="Item not found")
            return {"ids": updated_item.modified_count}

        @self.router.put(f"{self.prefix}-update-field-many")
        async def update_field_many(key_filter_queries: List[key_filter_model], data: dict):
            """
            Update a field of multiple items.

            Args:
                key_filter_queries (List[key_filter_model]): The list of key filter queries.
                data (dict): The data to update.

            Returns:
                dict: A success message.
            """
            key_filter_dicts = [BaseQuery.extract_filter(query) for query in key_filter_queries]
            await self.service.update_field_many(key_filter_dicts, data)
            return {"detail": "Item updated successfully"}

        @self.router.delete(f"{self.prefix}-delete-many/")
        async def delete_many(key_filter_queries: List[key_filter_model]):
            """
            Delete multiple items based on a list of dynamically defined query filters.

            Args:
                key_filter_queries (List[key_filter_model]): The list of key filter queries.

            Returns:
                dict: A success message.
            """
            # Extract filters from each key_filter_model instance
            key_filters = [BaseQuery.extract_filter(query) for query in key_filter_queries]

            # Pass the extracted filters to the service
            await self.service.delete_many(key_filters)
            return {"detail": "Items deleted successfully"}