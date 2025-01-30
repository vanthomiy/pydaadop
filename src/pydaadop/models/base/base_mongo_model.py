from datetime import datetime

from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional, List, Dict, Any

# Create a type alias for ObjectId
PyObjectId = str


class BaseMongoModel(BaseModel):
    # This maps _id from MongoDB to id in your application code
    id: Optional[PyObjectId] = Field(default_factory=lambda: str(ObjectId()), alias="_id")

    class Config:
        # Allow aliasing and arbitrary types like ObjectId
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str  # Ensures that ObjectId is serialized as string
        }

    def model_dump(self, *args, **kwargs):
        # Serialize with conditions: only include 'id' if it is not None
        data = super().model_dump()

        # Convert datetime fields to string (ISO 8601 format)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()  # Convert datetime to string in ISO format
            elif isinstance(value, ObjectId):
                data[key] = str(value)  # Convert ObjectId to string
        # extract ignore_id from args
        ignore_id = kwargs.get('ignore_id', False)

        # If 'id' is None, exclude it from the serialized output
        if self.id is not None and not ignore_id:
            data["_id"] = self.id
        data.pop("id", None)

        return data

    @staticmethod
    def create_index() -> List[str]:
        return ["id"]

    def model_dump_keys(self, *args, **kwargs) -> Dict[str, Any]:
        # Get the index fields from the model's create_index method
        index_keys = self.create_index()

        if "id" in index_keys:
            index_keys.remove("id")
            index_keys.append("_id")

        # Serialize the model and filter only the indexed fields
        serialized_data = self.model_dump(*args, **kwargs)

        # Select only the indexed fields
        filtered_data = {key: serialized_data[key] for key in index_keys if key in serialized_data}


        return filtered_data
