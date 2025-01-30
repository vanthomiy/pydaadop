from typing import Type, TypeVar, List
from fastapi import HTTPException, Depends
from pymongo.results import InsertManyResult, BulkWriteResult

from ...models.base import BaseMongoModel
from ...queries.base.base_query import BaseQuery
from ...services.bulk.bulk_read_write_service import BulkReadWriteService
from ...services.interface.bulk_read_write_service_interface import BulkReadWriteServiceInterface
from pydantic import BaseModel
from typing_extensions import override

from ..base.base_read_write_route import BaseReadWriteRouter

T = TypeVar("T", bound=BaseMongoModel)  # Generic type for the model class

class BulkReadWriteRouter(BaseReadWriteRouter[T]):
    def __init__(self, model: Type[T], service: BulkReadWriteServiceInterface = None):
        self.name = "bulk"
        self.service = service if service else BulkReadWriteService(model)
        super().__init__(model, self.service)

    @override
    def setup_routes(self):
        super().setup_routes()
        key_filter_model = self.service.create_key_filter()
        model = self.model  # Store the model locally for static use

        @self.router.post(f"{self.prefix}-insert-many")
        async def create_many(items: List[model]) -> dict:
            created_item = await self.service.create_many(items)
            return {"ids": created_item.inserted_ids}

        @self.router.put(f"{self.prefix}-update-many")
        async def update_many(items: List[model]) -> dict:
            updated_item = await self.service.update_many(items)
            if not updated_item:
                raise HTTPException(status_code=404, detail="Item not found")
            return {"ids": updated_item.modified_count}

        @self.router.put(f"{self.prefix}-update-field-many")
        async def update_field_many(key_filter_queries: List[key_filter_model], data: dict):
            key_filter_dicts = [BaseQuery.extract_filter(query) for query in key_filter_queries]
            await self.service.update_field_many(key_filter_dicts, data)
            return {"detail": "Item updated successfully"}


        @self.router.delete(f"{self.prefix}-delete-many/")
        async def delete_many(key_filter_queries: List[key_filter_model]):
            """
            Delete multiple items based on a list of dynamically defined query filters.
            """
            # Extract filters from each key_filter_model instance
            key_filters = [BaseQuery.extract_filter(query) for query in key_filter_queries]

            # Pass the extracted filters to the service
            await self.service.delete_many(key_filters)
            return {"detail": "Items deleted successfully"}