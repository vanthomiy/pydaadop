from typing import Dict, TypeVar, Type, cast

from .base_api_client import BaseApiClient
from ..api_clients.many_read_write_api_client import ManyReadWriteApiClient
from ..api_clients.read_api_client import ReadApiClient
from ..api_clients.read_write_api_client import ReadWriteApiClient
from ..models.base import BaseMongoModel

T = TypeVar("T", bound=BaseMongoModel)

class ClientFactory:
    def __init__(self, base_url: str, headers: Dict[str, str] = None):
        self.base_url = base_url
        self.headers = headers
        self.clients: Dict[Type[BaseMongoModel], BaseApiClient] = {}

    def get_read_client(self, model_class: Type[T]) -> ReadApiClient[T]:
        if model_class not in self.clients:
            self.clients[model_class] = ReadApiClient(self.base_url, model_class, self.headers)
        return cast(ReadApiClient[T], self.clients[model_class])

    def get_read_write_client(self, model_class: Type[T]) -> ReadWriteApiClient[T]:
        if model_class not in self.clients:
            self.clients[model_class] = ReadWriteApiClient(self.base_url, model_class, self.headers)
        return cast(ReadWriteApiClient[T], self.clients[model_class])

    def get_many_read_write_client(self, model_class: Type[T]) -> ManyReadWriteApiClient[T]:
        if model_class not in self.clients:
            self.clients[model_class] = ManyReadWriteApiClient(self.base_url, model_class, self.headers)
        return cast(ManyReadWriteApiClient[T], self.clients[model_class])