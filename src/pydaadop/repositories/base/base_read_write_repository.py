from typing import Type, TypeVar, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from .base_read_repository import BaseReadRepository
from ...models.base import BaseMongoModel

T = TypeVar("T", bound=BaseMongoModel)


class BaseReadWriteRepository(BaseReadRepository[T]):
    def __init__(self, model: Type[T], collection: AsyncIOMotorCollection = None):
        super().__init__(model, collection)

    async def create(self, item: T) -> T:
        result = await self.collection.insert_one(item.model_dump())
        item.id = str(result.inserted_id)  # Ensure the model has an 'id' field
        return item

    async def update(self, keys_filter_query: dict, item_data: T) -> Optional[T]:
        await self.collection.update_one(keys_filter_query, {"$set": item_data.model_dump(ignore_id=True)})
        return await self.get_by_id(keys_filter_query)

    async def delete(self, keys_filter_query: dict) -> None:
        await self.collection.delete_one(keys_filter_query)
