from typing import Type, TypeVar
from fastapi import HTTPException, Depends

from ...models.base import BaseMongoModel
from ...queries.base.base_query import BaseQuery
from ...services.base.base_read_write_service import BaseReadWriteService
from ...services.interface.read_write_service_interface import ReadWriteServiceInterface
from typing_extensions import override

from .base_read_route import BaseReadRouter

T = TypeVar("T", bound=BaseMongoModel)  # Generic type for the model class


class BaseReadWriteRouter(BaseReadRouter[T]):
    def __init__(self, model: Type[T], service: ReadWriteServiceInterface = None):
        self.service = service if service else BaseReadWriteService(model)
        super().__init__(model, self.service)

    @override
    def setup_routes(self):
        key_filter_model = self.service.create_key_filter()
        super().setup_routes()
        model = self.model  # Store the model locally for static use

        @self.router.post(f"{self.prefix}/")
        async def create_item(item: model):
            created_item = await self.service.create(item)
            return created_item


        @self.router.put(f"{self.prefix}/", response_model=model)
        async def update_item(item: model):
            updated_item = await self.service.update(item)
            if not updated_item:
                raise HTTPException(status_code=404, detail="Item not found")
            return updated_item

        @self.router.delete(f"{self.prefix}/")
        async def delete_item(key_filter_query: key_filter_model = Depends()):
            key_filter_dict = BaseQuery.extract_filter(key_filter_query)
            await self.service.delete(key_filter_dict)
            return {"detail": "Item deleted successfully"}

