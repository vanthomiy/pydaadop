from pydaadop.api_clients.base_api_client import T
from .read_write_api_client import ReadWriteApiClient
from typing import List, Dict, TypeVar
from ..models.base import BaseMongoModel

class ManyReadWriteApiClient(ReadWriteApiClient[T]):
    """
    A client for performing batch read and write operations on a specific model.

    Args:
        base_url (str): The base URL for the API.
        model_class (Type[T]): The model class to be used.
        headers (Dict[str, str], optional): Additional headers for the requests.

    """

    def insert_many(self, items: List[T]) -> Dict:
        """
        Inserts multiple items into the database.

        Args:
            items (List[T]): The items to be inserted.

        Returns:
            Dict: The response data from the database.

        Example:
            items = [MyModel(name="example1"), MyModel(name="example2")]
            response = client.insert_many(items)
        """
        if not items or len(items) == 0:
            return {}
        endpoint = self.model_class.__name__.lower() + "-insert-many"
        dict_items = [item.model_dump() for item in items]
        response_data = self._request("POST", endpoint, json=dict_items)
        return response_data

    def update_many(self, items: List[T]) -> Dict:
        """
        Updates multiple items in the database.

        Args:
            items (List[T]): The items to be updated.

        Returns:
            Dict: The response data from the database.

        Example:
            items = [client.get({"id": "123"}), client.get({"id": "456"})]
            for item in items:
                item.name = "new name"
            response = client.update_many(items)
        """
        if not items or len(items) == 0:
            return {}
        endpoint = self.model_class.__name__.lower() + "-update-many"
        items_dict = [item.model_dump() for item in items]
        response_data = self._request("PUT", endpoint, json=items_dict)
        return response_data

    def update_field_many(self, items: List[dict], data: dict) -> Dict:
        """
        Updates specific fields of multiple items in the database.

        Args:
            items (List[dict]): The items to be updated.
            data (dict): The fields to be updated.

        Returns:
            Dict: The response data from the database.

        Example:
            items = [{"id": "123"}, {"id": "456"}]
            data = {"name": "new name"}
            response = client.update_field_many(items, data)
        """
        if not items or len(items) == 0:
            return {}
        endpoint = self.model_class.__name__.lower() + "-update-field-many"
        data_dict = {"data": data}
        items_dict = [item for item in items]
        combined = {**data_dict, **items_dict}
        response_data = self._request("PUT", endpoint, json=combined)
        return response_data

    def delete_many(self, items: List[dict]) -> None:
        """
        Deletes multiple items from the database.

        Args:
            items (List[dict]): The items to be deleted.

        Example:
            items = [{"id": "123"}, {"id": "456"}]
            client.delete_many(items)
        """
        if not items or len(items) == 0:
            return
        items = [item for item in items if item != {}]
        if not items or len(items) == 0:
            return
        endpoint = self.model_class.__name__.lower() + "-delete-many"
        self._request("DELETE", endpoint, json=items)