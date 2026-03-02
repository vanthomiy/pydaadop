from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from bson import ObjectId
from typing import Optional, List, Dict, Any
import string


# PyObjectId: pydantic-friendly ObjectId type
class PyObjectId(ObjectId):
    """A wrapper type that tells pydantic how to validate/serialize Mongo ObjectId.

    Accepts bson.ObjectId or hex strings. Internally values are stored as bson.ObjectId instances.
    Compatible with Pydantic v2 via core/json schema hooks.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            s = v.strip()
            if len(s) >= 2 and ((s[0] == s[-1]) and s[0] in ("'", '"')):
                s = s[1:-1].strip()
            if len(s) == 24 and all(c in string.hexdigits for c in s):
                try:
                    return ObjectId(s)
                except Exception:
                    pass
        raise TypeError("value is not a valid ObjectId or hex string")

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        # Prefer pydantic_core first (more likely present in minimal images),
        # then fall back to pydantic wrapper if available.
        try:
            from pydantic_core import core_schema
        except Exception:
            try:
                from pydantic import core_schema
            except Exception:
                raise RuntimeError(
                    "pydantic v2 is required for PyObjectId, please install pydantic>=2"
                )

        def _validate(v, info):
            if isinstance(v, ObjectId):
                return v
            try:
                return ObjectId(str(v))
            except Exception:
                raise TypeError("value is not a valid ObjectId or hex string")

        return core_schema.no_info_plain_validator_function(_validate)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema_, handler=None):
        return {"type": "string", "format": "objectid"}


class BaseMongoModel(BaseModel):
    """
    Base model for MongoDB documents using Pydantic.

    Attributes:
        id (Optional[PyObjectId]): The unique identifier for the document, mapped from MongoDB's _id.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )

    # store _id as a real ObjectId internally; serialize to str when encoding to JSON
    id: Optional[PyObjectId] = Field(default_factory=lambda: ObjectId(), alias="_id")

    def model_dump(self, *args: dict, **kwargs: dict) -> Dict[str, Any]:
        """
        Serialize the model to a dictionary, with special handling for datetime and ObjectId fields.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Dict[str, Any]: The serialized model as a dictionary.
        """
        # Serialize with conditions: only include 'id' if it is not None
        data = super().model_dump()

        # Convert datetime fields to string (ISO 8601 format)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = (
                    value.isoformat()
                )  # Convert datetime to string in ISO format
            elif isinstance(value, ObjectId):
                data[key] = str(value)  # Convert ObjectId to string
        # extract ignore_id from args
        ignore_id = kwargs.get("ignore_id", False)

        # If 'id' is None, exclude it from the serialized output
        if self.id is not None and not ignore_id:
            data["_id"] = self.id
        data.pop("id", None)

        return data

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
