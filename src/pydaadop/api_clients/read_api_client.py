from .base_api_client import BaseApiClient
from typing import TypeVar
from ..models.base import BaseMongoModel

T = TypeVar("T", bound=BaseMongoModel)

class ReadApiClient(BaseApiClient[T]):
    pass