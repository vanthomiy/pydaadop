import asyncio
import inspect
import logging
from typing import TypeVar, Type, Optional, List

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
            # Attempt to ensure indexes immediately (useful in tests that provide an AsyncMock)
            # Note: when tests provide a synchronous pymongo collection this will be a no-op.
            self.ensure_indexes()
            return

        # Defer creating the Motor client/collection until first use to avoid
        # side-effects at import time. Store parameters for lazy init.
        self._database_name = database_name
        self._provided_client = client
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection: Optional[AsyncIOMotorCollection] = None

    def _ensure_connection(self):
        """Lazily create the Motor client, database and collection if not present."""
        if self.collection is not None:
            return

        uri = env_manager.get_mongo_uri()
        self.client = self._provided_client if self._provided_client is not None else AsyncIOMotorClient(uri)
        self.db = self.client[self._database_name]
        self.collection = self.db[self.model.__name__]
        # Ensure indexes after we have a real collection
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
        index_field_names: List[str] = ["_id" if k == "id" else k for k in keys]
        index_spec = [(field, ASCENDING) for field in index_field_names]

        # Build a deterministic name for the index using the actual field names
        index_name = f"unique_{self.model.__name__}_" + "_".join(index_field_names)

        # Call create_index. The collection implementation may return either an awaitable
        # (Motor) or a synchronous result (pymongo). If it's synchronous, nothing to do.
        try:
            maybe_awaitable = self.collection.create_index(index_spec, unique=True, name=index_name)
        except Exception as e:
            logging.warning("Failed initiating index creation for %s: %s", self.model.__name__, e)
            return

        # If the result is not awaitable (synchronous driver), return early
        if not inspect.isawaitable(maybe_awaitable):
            return

        # If it's awaitable (Motor), schedule or run it depending on loop state. Use
        # asyncio.ensure_future which accepts both coroutines and futures when a loop
        # is running; fall back to asyncio.run when no loop is present.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop: run the awaitable synchronously so indexes are created now
            try:
                asyncio.run(maybe_awaitable)
            except Exception as e:  # don't let index errors break initialization
                logging.warning("Failed creating index for %s synchronously: %s", self.model.__name__, e)
        else:
            try:
                # ensure_future schedules the awaitable on the running loop and accepts
                # coroutines or Future-like objects (avoids 'coroutine expected, got Future')
                asyncio.ensure_future(maybe_awaitable)
            except Exception as e:
                logging.warning("Failed scheduling index creation for %s: %s", self.model.__name__, e)
