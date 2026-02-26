"""
This module provides the BaseRouter class, which serves as a base class for setting up
routes for MongoDB models.

Classes:
    BaseRouter: A base router class for setting up routes for MongoDB models.
"""

from abc import abstractmethod
from typing import Type, TypeVar, Generic
from fastapi import APIRouter

from ...models.base import BaseMongoModel

T = TypeVar("T", bound=BaseMongoModel)  # Generic type for the model class

class BaseRouter(Generic[T]):
    """
    A base router class for setting up routes for MongoDB models.

    Attributes:
        tags (List[str]): The tags for the router.
        router (APIRouter): The FastAPI router.
        model (Type[T]): The MongoDB model type.
        prefix (str): The prefix for the routes.
    """

    def __init__(self, model: Type[T]):
        """
        Initialize the BaseRouter.

        Args:
            model (Type[T]): The MongoDB model type.
        """
        self.tags = [model.__name__]
        self.router = APIRouter(tags=self.tags)
        self.model = model
        # Router paths are written relative to a base prefix derived from the
        # model name (e.g. '/product'). This preserves the historical behavior
        # where routes are reachable under '/<model-name>/' when the router is
        # included without an explicit prefix (tests rely on this). When a
        # caller includes the APIRouter with an explicit prefix they should
        # avoid duplicating the model segment to prevent double paths.
        # Normalize model name to a short path segment: strip trailing 'model'
        # so CustomModel -> '/custom' and DemoProduct -> '/demoproduct'.
        name = model.__name__.lower()
        if name.endswith("model"):
            name = name[:-5]
        self.prefix = f"/{name}"
        self.setup_routes()

    @abstractmethod
    def create_openapi_schema(self, schema: dict):
        """
        Create the OpenAPI schema for the routes.

        Args:
            schema (dict): The OpenAPI schema.
        """
        pass

    @abstractmethod
    def setup_routes(self):
        """
        Set up the routes for the MongoDB model.
        """
        pass


