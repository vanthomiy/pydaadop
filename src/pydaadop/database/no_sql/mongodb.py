import asyncio
import logging
from typing import TypeVar, Type, Optional

from ...models.base import BaseMongoModel
from ...utils.environment import env_manager

# Initialize logging configuration
logging.basicConfig(level=logging.INFO)

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ASCENDING

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
    def __init__(self, model: Type[T], database_name: str = "deriven-database", client: Optional[AsyncIOMotorClient] = None, collection: Optional[AsyncIOMotorCollection] = None):
        """
        Initializes the BaseMongoDatabase instance.

        Args:
            model (Type[T]): The model class that represents the MongoDB collection.
            database_name (str): The name of the database to connect to. Defaults to "deriven-database".
        """
        self.model = model

        # If a collection is provided, use it directly (useful for tests and DI).
        if collection is not None:
            self.client = client
            self.db = None
            self.collection = collection
            # Attempt to ensure indexes immediately (may run synchronously)
            self.ensure_indexes()
            return

        # Otherwise build a motor client using environment configuration
        uri = env_manager.get_mongo_uri()
        self.client: AsyncIOMotorClient = client if client is not None else AsyncIOMotorClient(uri)
        self.db: AsyncIOMotorDatabase = self.client[database_name]
        self.collection: AsyncIOMotorCollection = self.db[self.model.__name__]

        # Ensure indexes (best-effort; may run synchronously or schedule on running loop)
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
        # Get the index fields list from the model
        keys = self.model.create_index() or []

        # No meaningful keys to index
        if not keys or (len(keys) == 1 and keys[0] == "id"):
            return

        # Map 'id' to MongoDB's '_id' and build the index spec as list of (field, direction)
        index_spec = []
        for k in keys:
            field_name = "_id" if k == "id" else k
            index_spec.append((field_name, ASCENDING))

        # Build a deterministic name for the index
        index_name = f"unique_{self.model.__name__}_" + "_".join(keys)

        # Create the index. Motor's create_index is asynchronous; handle both cases:
        coro = self.collection.create_index(index_spec, unique=True, name=index_name)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop: run the coroutine synchronously (blocking) so that indexes are created during init
            try:
                asyncio.run(coro)
            except Exception as e:  # don't let index errors break initialization
                logging.warning("Failed creating index for %s synchronously: %s", self.model.__name__, e)
        else:
            # Running in an event loop — schedule the index creation
            try:
                loop.create_task(coro)
            except Exception as e:
                logging.warning("Failed scheduling index creation for %s: %s", self.model.__name__, e)
