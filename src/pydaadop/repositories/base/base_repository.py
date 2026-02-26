"""
This module provides the BaseRepository class, which serves as a base repository
for MongoDB models.

Classes:
    BaseRepository: A base repository class for MongoDB models.
"""

from typing import Type, TypeVar, Generic

from motor.motor_asyncio import AsyncIOMotorCollection

from ...models.base import BaseMongoModel
from ...database.no_sql import BaseMongoDatabase

T = TypeVar("T", bound=BaseMongoModel)

class BaseRepository(Generic[T]):
    """
    A base repository class for MongoDB models.

    Attributes:
        model (Type[T]): The MongoDB model type.
        collection (AsyncIOMotorCollection): The MongoDB collection.
    """

    def __init__(self, model: Type[T], collection: AsyncIOMotorCollection = None):
        """
        Initialize the BaseRepository.

        Args:
            model (Type[T]): The MongoDB model type.
            collection (AsyncIOMotorCollection, optional): The MongoDB collection. Defaults to None.
        """
        self.model = model
        if collection is not None:
            self.collection = collection
        else:
            # Lazily initialize the database/collection; creating BaseMongoDatabase
            # may attempt to connect to MongoDB — this keeps behavior explicit and
            # test-friendly while preserving the original semantics.
            db = BaseMongoDatabase(model)
            self.collection = db.collection
