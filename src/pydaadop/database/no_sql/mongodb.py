import asyncio
import logging
from typing import TypeVar, Type

from ...models.base import BaseMongoModel
from ...utils.environment import env_manager

# Initialize logging configuration
logging.basicConfig(level=logging.INFO)

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

T = TypeVar("T", bound=BaseMongoModel)

class BaseMongoDatabase:
    def __init__(self, model: Type[T], database_name: str = "deriven-database"):
        self.model = model
        uri = env_manager.get_mongo_uri()
        self.client: AsyncIOMotorClient  = AsyncIOMotorClient(uri)
        self.db: AsyncIOMotorDatabase = self.client[database_name]
        self.collection: AsyncIOMotorCollection = self.db[self.model.__name__]
        self.ensure_indexes()

    def ensure_indexes(self):
        # Get the index based on the model
        keys = self.model.create_index()

        # if only _id we do not create an index
        if len(keys) == 1 and "id" in keys:
            return
        elif "id" in keys:
            keys.remove("id")
            keys.append("_id")

        # Ensure a unique index
        self.collection.create_index(
            keys,
            unique=True,
            name=f"unique_{self.model.__name__}"
        )
