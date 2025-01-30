from abc import abstractmethod
from typing import Type, TypeVar, Generic
from fastapi import APIRouter

from ...models.base import BaseMongoModel

T = TypeVar("T", bound=BaseMongoModel)  # Generic type for the model class

class BaseRouter(Generic[T]):
    def __init__(self, model: Type[T]):
        self.tags = [model.__name__]
        self.router = APIRouter(tags=self.tags)
        self.model = model
        self.prefix = f"/{model.__name__.lower()}"  # Store the prefix
        self.setup_routes()

    @abstractmethod
    def create_openapi_schema(self, schema: dict):
        pass

    @abstractmethod
    def setup_routes(self):
        pass


