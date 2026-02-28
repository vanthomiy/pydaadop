from typing import List, Optional
import string

from bson import ObjectId


class BaseListFilter:
    """
    BaseListFilter class for filtering lists of items by a specific key.

    Attributes:
        value (Optional[List[str]]): The list of values to filter by.
        key (str): The key to filter by (default is "_id").
    """

    def __init__(self, value: Optional[List[str]], key: str = "_id"):
        self.key = key
        self.value = value

    def to_mongo_filter(self, convert_objectid: Optional[bool] = None) -> dict:
        """
        Convert the filter to a MongoDB filter.

        Returns:
            dict: The MongoDB filter.
        """
        # If no values provided, return an empty filter
        if not self.value:
            return {}

        def _safe_maybe_objectid(v):
            # Already an ObjectId -> keep
            if isinstance(v, ObjectId):
                return v

            # Caller explicitly asked to not convert -> keep as-is
            if convert_objectid is False:
                return v

            # If caller explicitly asked to convert, try to convert any string
            if convert_objectid is True and isinstance(v, str):
                try:
                    return ObjectId(v)
                except Exception:
                    return v

            # Heuristic (default behavior when convert_objectid is None):
            # convert strings that look like 24-char hex ObjectId values
            if (
                isinstance(v, str)
                and len(v) == 24
                and all(c in string.hexdigits for c in v)
            ):
                try:
                    return ObjectId(v)
                except Exception:
                    return v

            # Leave everything else unchanged
            return v

        converted_list = [_safe_maybe_objectid(v) for v in self.value]
        return {self.key: {"$in": converted_list}}
