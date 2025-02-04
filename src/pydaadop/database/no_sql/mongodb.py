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
    """
    Base class for MongoDB database operations.

    This class provides basic functionality to interact with a MongoDB database using
    Motor, an asynchronous MongoDB driver for Python.

    Attributes:
        model (Type[T]): The model class that represents the MongoDB collection.
        database_name (str): The name of the database to connect to.
        client (AsyncIOMotorClient): The Motor client instance.
        db (AsyncIOMotorDatabase): The Motor database instance.
        collection (AsyncIOMotorCollection): The Motor collection instance.

    Example:
        ```python
        from myapp.models import MyModel
        from myapp.database.no_sql.mongodb import BaseMongoDatabase

        db = BaseMongoDatabase(model=MyModel, database_name="my_database")
        ```
    """
    def __init__(self, model: Type[T], database_name: str = "deriven-database"):
        """
        Initializes the BaseMongoDatabase instance.

        Args:
            model (Type[T]): The model class that represents the MongoDB collection.
            database_name (str): The name of the database to connect to. Defaults to "deriven-database".
        """
        self.model = model
        uri = env_manager.get_mongo_uri()
        self.client: AsyncIOMotorClient  = AsyncIOMotorClient(uri)
        self.db: AsyncIOMotorDatabase = self.client[database_name]
        self.collection: AsyncIOMotorCollection = self.db[self.model.__name__]
        self.ensure_indexes()

    def ensure_indexes(self):
        """
        Ensures that the necessary indexes are created for the collection.

        This method retrieves the index keys from the model and creates a unique index
        for the collection. If the only key is "id", no index is created. If "id" is
        present among other keys, it is replaced with "_id".

        Example:
            ```python
            db.ensure_indexes()
            ```
        """
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
