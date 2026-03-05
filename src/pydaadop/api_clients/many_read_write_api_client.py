from pydaadop.api_clients.base_api_client import T
from .read_write_api_client import ReadWriteApiClient
from typing import List, Dict, TypeVar, Any
from ..models.base import BaseMongoModel


def _extract_ids_from_response(resp: Any) -> List[Any]:
    """Extract a flat list of ids from common server responses.

    Supported shapes:
    - dict with key 'ids' or 'inserted_ids' -> the list value
    - an object with attribute 'inserted_ids' (best-effort)
    - list of scalars or list of dicts (try to read 'id' or '_id')

    Returns an empty list if no candidate ids are found.
    """
    try:
        # dict responses like {"ids": [...]} or {"inserted_ids": [...]}
        if isinstance(resp, dict):
            ids = resp.get("ids") or resp.get("inserted_ids")
            if isinstance(ids, list):
                return ids
            # occasionally APIs return list of inserted documents under other keys
            # not attempting to guess too much here — return empty when not a list
            return []

        # some callers may pass through driver objects; try attribute access
        if hasattr(resp, "inserted_ids"):
            try:
                return list(resp.inserted_ids)
            except Exception:
                pass

        # list response: either list of scalars or list of dicts
        if isinstance(resp, list):
            out: List[Any] = []
            for el in resp:
                try:
                    if isinstance(el, dict):
                        if "id" in el:
                            out.append(el["id"])
                        elif "_id" in el:
                            out.append(el["_id"])
                        elif "inserted_id" in el:
                            out.append(el["inserted_id"])
                        else:
                            # fallback: append the whole element
                            out.append(el)
                    else:
                        # scalar value (string/number), use as-is
                        out.append(el)
                except Exception:
                    out.append(el)
            return out
    except Exception:
        pass
    return []

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
        dict_items = [item.model_dump(ignore_id=True) for item in items]
        response_data = self._request("POST", endpoint, json=dict_items)

        # --- map returned ids back onto passed-in items (best-effort) ---
        try:
            ids = _extract_ids_from_response(response_data)
            if ids:
                n = min(len(ids), len(items))
                for i in range(n):
                    try:
                        # Use str(...) to normalize ObjectId-like values to string
                        setattr(items[i], "id", str(ids[i]))
                    except Exception:
                        # best-effort: ignore mapping errors
                        pass
        except Exception:
            # preserve original behavior on any error
            pass

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

    
    def delete_many(self, items: List[T]) -> None:
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
        
        # build the keys
        keys = []
        for item in items:
            try:
                keys.append(item.model_dump_keys())
            except Exception:
                pass
        
        return self.delete_many(keys)
