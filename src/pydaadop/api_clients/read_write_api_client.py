from .read_api_client import T, ReadApiClient
from typing import TypeVar, Type, Dict, Optional, Any

from ..models.base import BaseMongoModel


class ReadWriteApiClient(ReadApiClient[T]):
    """
    A client for performing read and write operations on a specific model.

    Args:
        base_url (str): The base URL for the API.
        model_class (Type[T]): The model class to be used.
        headers (Dict[str, str], optional): Additional headers for the requests.

    """

    def insert(self, item: T) -> T:
        """
        Inserts a new item into the database.

        Args:
            item (T): The item to be inserted.

        Returns:
            T: The inserted item with updated fields from the database.

        Example:
            new_item = MyModel(name="example")
            inserted_item = client.insert(new_item)
        """
        endpoint = self.model_class.__name__.lower()
        item_dict = item.model_dump(ignore_id=True)
        response_data = self._request("POST", endpoint, json=item_dict)
        return self.model_class(**response_data)

    def update(self, item: T) -> T:
        """
        Updates an existing item in the database.

        Args:
            item (T): The item to be updated.

        Returns:
            T: The updated item with fields from the database.

        Example:
            existing_item = client.get({"id": "123"})
            existing_item.name = "new name"
            updated_item = client.update(existing_item)
        """
        endpoint = f"{self.model_class.__name__.lower()}"
        item_dict = item.model_dump()
        response_data = self._request("PUT", endpoint, json=item_dict)
        return self.model_class(**response_data)

    def delete(self, key_filter_query: Optional[Dict[str, Any] | str | T] = None) -> None:
        """
        Deletes an item from the database.

        Args:
            key_filter_query (Optional[Dict[str, Any]]): The query to filter the item to be deleted.

        Example:
            client.delete({"id": "123"})
        """
        # Normalize input: accept an id string, a dict filter, or a model instance
        if key_filter_query is None:
            raise ValueError("delete requires a filter dict, id string, or model instance")

        # If a model instance was provided, convert to key filter dict
        try:
            # model instances from pydantic will have `model_dump_keys`
            if hasattr(key_filter_query, "model_dump_keys"):
                key_filter_query = key_filter_query.model_dump_keys()
        except Exception:
            pass

        # If provided a bare id string, wrap as _id
        if isinstance(key_filter_query, str):
            key_filter_query = {"_id": key_filter_query}

        # Use the public parse_query to build params
        _params = self.parse_query(key_filter_query=key_filter_query)
        endpoint = f"{self.model_class.__name__.lower()}"
        self._request("DELETE", endpoint, params=_params)
