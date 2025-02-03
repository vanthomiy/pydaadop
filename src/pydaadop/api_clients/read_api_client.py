from .base_api_client import T, BaseApiClient
from typing import TypeVar
from ..models.base import BaseMongoModel

class ReadApiClient(BaseApiClient[T]):
    """
    A client for performing read operations on a specific model.

    Args:
        base_url (str): The base URL for the API.
        model_class (Type[T]): The model class to be used.
        headers (Dict[str, str], optional): Additional headers for the requests.
    """
    pass