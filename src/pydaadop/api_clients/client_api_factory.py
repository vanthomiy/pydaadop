from typing import Dict, TypeVar, Type, cast

from .base_api_client import T, BaseApiClient
from ..api_clients.many_read_write_api_client import ManyReadWriteApiClient
from ..api_clients.read_api_client import ReadApiClient
from ..api_clients.read_write_api_client import ReadWriteApiClient
from ..models.base import BaseMongoModel


class ClientFactory:
    """
    A factory for creating API clients for different models.

    Args:
        base_url (str): The base URL for the API.
        headers (Dict[str, str], optional): Additional headers for the requests.
    """

    def __init__(self, base_url: str, headers: Dict[str, str] = None):
        self.base_url = base_url
        self.headers = headers
        self.clients: Dict[Type[BaseMongoModel], BaseApiClient] = {}

    def get_read_client(self, model_class: Type[T]) -> ReadApiClient[T]:
        """
        Returns a read client for the specified model.

        Args:
            model_class (Type[T]): The model class to be used.

        Returns:
            ReadApiClient[T]: The read client for the specified model.

        Example:
            factory = ClientFactory("http://localhost:8000/")
            read_client = factory.get_read_client(MyModel)
        """
        if model_class not in self.clients:
            self.clients[model_class] = ReadApiClient(self.base_url, model_class, self.headers)
        return cast(ReadApiClient[T], self.clients[model_class])

    def get_read_write_client(self, model_class: Type[T]) -> ReadWriteApiClient[T]:
        """
        Returns a read-write client for the specified model.

        Args:
            model_class (Type[T]): The model class to be used.

        Returns:
            ReadWriteApiClient[T]: The read-write client for the specified model.

        Example:
            factory = ClientFactory("http://localhost:8000/")
            read_write_client = factory.get_read_write_client(MyModel)
        """
        if model_class not in self.clients:
            self.clients[model_class] = ReadWriteApiClient(self.base_url, model_class, self.headers)
        return cast(ReadWriteApiClient[T], self.clients[model_class])

    def get_many_read_write_client(self, model_class: Type[T]) -> ManyReadWriteApiClient[T]:
        """
        Returns a many read-write client for the specified model.

        Args:
            model_class (Type[T]): The model class to be used.

        Returns:
            ManyReadWriteApiClient[T]: The many read-write client for the specified model.

        Example:
            factory = ClientFactory("http://localhost:8000/")
            many_read_write_client = factory.get_many_read_write_client(MyModel)
        """
        if model_class not in self.clients:
            self.clients[model_class] = ManyReadWriteApiClient(self.base_url, model_class, self.headers)
        return cast(ManyReadWriteApiClient[T], self.clients[model_class])