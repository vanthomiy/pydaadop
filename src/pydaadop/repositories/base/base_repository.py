from typing import Type, TypeVar, Generic

from motor.motor_asyncio import AsyncIOMotorCollection

from ...models.base import BaseMongoModel
from ...database.no_sql import BaseMongoDatabase

T = TypeVar("T", bound=BaseMongoModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], collection: AsyncIOMotorCollection = None):
        self.model = model
        self.collection = collection if collection else BaseMongoDatabase(model).collection
