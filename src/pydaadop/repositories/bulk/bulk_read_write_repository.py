from typing import Type, TypeVar, Generic, List, Optional, Dict

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne
from pymongo.results import InsertManyResult, DeleteResult, BulkWriteResult

from ..base.base_read_write_repository import BaseReadWriteRepository
from ...models.base import BaseMongoModel

T = TypeVar("T", bound=BaseMongoModel)


class BulkReadWriteRepository(BaseReadWriteRepository[T]):
    def __init__(self, model: Type[T], collection: AsyncIOMotorCollection = None):
        super().__init__(model, collection)

    async def create_many(self, items: List[T]) -> InsertManyResult:
        # insert many items into the collection with bulk write
        serialized_items = [item.model_dump(by_alias=True) for item in items]
        return await self.collection.insert_many(serialized_items, ordered=False)

    async def update_many(self, items: List[T]) -> BulkWriteResult:
        # update many items in the collection with bulk write
        bulk_write_operations = [UpdateOne(item.model_dump_keys(), {"$set": item.model_dump()}) for item in items]
        return await self.collection.bulk_write(bulk_write_operations)

    async def update_field_many(self, keys_filter_query: List[dict], data: dict) -> BulkWriteResult:
        # update field of many items in the collection with bulk write
        bulk_write_operations = [UpdateOne(key_filter, {"$set": data}) for key_filter in keys_filter_query]
        return await self.collection.bulk_write(bulk_write_operations)

    async def delete_many(self, keys_filter_query: List[dict]) -> DeleteResult:
        # delete many items from the collection with bulk write where any of the keys_filter_query matches
        return await self.collection.delete_many({"$or": keys_filter_query})
