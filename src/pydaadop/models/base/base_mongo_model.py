from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from bson import ObjectId
from typing import Optional, List, Dict, Any
import base64
import uuid
from decimal import Decimal
from enum import Enum
from datetime import date, time


class BaseMongoModel(BaseModel):
    """
    Base model for MongoDB documents using Pydantic.

    Attributes:
        id (Optional[str]): The unique identifier for the document, mapped from MongoDB's _id.
            By default a new ObjectId hex string is generated.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )

    # store _id as a string (ObjectId hex) by default — simplifies serialization
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")

    def __init__(self, **data):
        # Coerce any incoming ObjectId values to hex strings for consistency
        if "_id" in data and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
        if "id" in data and isinstance(data["id"], ObjectId):
            data["id"] = str(data["id"])
        super().__init__(**data)

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Serialize the model to a dictionary, with special handling for datetime and ObjectId fields.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Dict[str, Any]: The serialized model as a dictionary.
        """
        # Pull out our special flag, pass the rest through to pydantic
        ignore_id = kwargs.pop("ignore_id", False)
        # Let pydantic perform its dump respecting caller kwargs
        try:
            data = super().model_dump(*args, **kwargs)
        except TypeError:
            # Older pydantic signatures? fall back without args
            data = super().model_dump()

        # Sanitize recursively to ensure JSON-safe primitives and detect cycles
        def _sanitize(obj, _seen=None, _depth=0):
            if _seen is None:
                _seen = set()
            # protect against pathological recursion
            if _depth > 200:
                return str(obj)

            # simple primitives
            if obj is None or isinstance(obj, (str, bool, int, float)):
                return obj

            # avoid revisiting same container
            oid = id(obj)
            if oid in _seen:
                return str(obj)
            _seen.add(oid)

            # pydantic models -> dict
            if isinstance(obj, BaseModel):
                try:
                    sub = obj.model_dump()
                except Exception:
                    _seen.discard(oid)
                    return str(obj)
                res = _sanitize(sub, _seen=_seen, _depth=_depth + 1)
                _seen.discard(oid)
                return res

            # dict -> sanitize keys and values
            if isinstance(obj, dict):
                out = {}
                for k, v in obj.items():
                    try:
                        key = str(k)
                    except Exception:
                        key = repr(k)
                    out[key] = _sanitize(v, _seen=_seen, _depth=_depth + 1)
                _seen.discard(oid)
                return out

            # sequences -> list
            if isinstance(obj, (list, tuple, set, frozenset)):
                out = [_sanitize(v, _seen=_seen, _depth=_depth + 1) for v in obj]
                _seen.discard(oid)
                return out

            # datetime/date/time -> iso
            if isinstance(obj, (datetime, date, time)):
                _seen.discard(oid)
                try:
                    return obj.isoformat()
                except Exception:
                    return str(obj)

            # bson ObjectId
            if isinstance(obj, ObjectId):
                _seen.discard(oid)
                return str(obj)

            # bytes -> base64
            if isinstance(obj, (bytes, bytearray)):
                try:
                    out = base64.b64encode(bytes(obj)).decode("ascii")
                except Exception:
                    out = str(obj)
                _seen.discard(oid)
                return out

            # Decimal -> string to avoid float precision loss
            if isinstance(obj, Decimal):
                _seen.discard(oid)
                return str(obj)

            # UUID -> string
            if isinstance(obj, uuid.UUID):
                _seen.discard(oid)
                return str(obj)

            # Enum -> value or name
            if isinstance(obj, Enum):
                _seen.discard(oid)
                return obj.value if hasattr(obj, "value") else str(obj)

            # fallback to string representation
            try:
                out = str(obj)
            except Exception:
                out = repr(obj)
            _seen.discard(oid)
            return out

        sanitized = _sanitize(data)

        # Ensure we always return a mapping
        if not isinstance(sanitized, dict):
            sanitized = {"value": sanitized}

        # If id exists and caller didn't ask to ignore it, expose as _id
        if self.id is not None and not ignore_id:
            sanitized["_id"] = str(self.id)
        # remove the plain 'id' key to keep API surface stable
        sanitized.pop("id", None)

        return sanitized

    @staticmethod
    def create_index() -> List[str]:
        """
        Define the index fields for the model.

        Returns:
            List[str]: A list of field names to be indexed.
        """
        return ["id"]

    def model_dump_keys(self, *args: dict, **kwargs: dict) -> Dict[str, Any]:
        """
        Serialize the model and filter only the indexed fields.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Dict[str, Any]: The serialized model with only the indexed fields.
        """
        # Get the index fields from the model's create_index method
        index_keys = self.create_index()

        if "id" in index_keys:
            index_keys.remove("id")
            index_keys.append("_id")

        # Serialize the model and filter only the indexed fields
        serialized_data = self.model_dump(*args, **kwargs)

        # Select only the indexed fields
        filtered_data = {
            key: serialized_data[key] for key in index_keys if key in serialized_data
        }

        return filtered_data
