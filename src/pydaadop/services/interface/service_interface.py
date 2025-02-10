"""
This module provides the ServiceInterface class, which defines the interface for service classes
that handle various operations on a model.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Type
from pydantic import BaseModel

from ...models.display import DisplayQueryInfo, DisplayItemInfo
from ...queries.base.base_list_filter import BaseListFilter
from ...queries.base.base_paging import BasePaging
from ...queries.base.base_range import BaseRange
from ...queries.base.base_select import BaseSelect
from ...queries.base.base_sort import BaseSort
from ...repositories.base.base_repository import BaseRepository

S = TypeVar('S', bound=BaseModel)

class ServiceInterface(ABC, Generic[S]):
    """
    Interface for service classes that handle various operations on a model.

    Attributes:
        model (Type[S]): The model class.
    """

    def __init__(self, model: Type[S]):
        """
        Initialize the ServiceInterface.

        Args:
            model (Type[S]): The model class.
        """
        self.model = model

    @classmethod
    def _update_filter_query(cls, filter_query: Dict = None, list_filter: BaseListFilter = None) -> Dict:
        """
        Update the filter query with additional filters.

        Args:
            filter_query (Dict, optional): The original filter query. Defaults to None.
            list_filter (BaseListFilter, optional): Additional filters to be applied. Defaults to None.

        Returns:
            Dict: The updated filter query.
        """
        if not filter_query and not list_filter:
            return {}
        if not filter_query:
            filter_query = {}
        if not list_filter:
            return filter_query

        # create a copy of the filter query because we don't want to modify the original
        filter_query_copy = filter_query.copy()

        filter_query_copy.update(list_filter.to_mongo_filter())

        return filter_query_copy

    @abstractmethod
    def create_filter(self) -> Type[BaseModel]:
        """
        Create a filter model.

        Returns:
            Type[BaseModel]: The filter model class.
        """
        pass

    @abstractmethod
    def create_key_filter(self) -> Type[BaseModel]:
        """
        Create a key filter model.

        Returns:
            Type[BaseModel]: The key filter model class.
        """
        pass

    @abstractmethod
    def create_sort(self) -> Type[BaseSort]:
        """
        Create a sort model.

        Returns:
            Type[BaseSort]: The sort model class.
        """
        pass

    @abstractmethod
    def create_range(self) -> Type[BaseRange]:
        """
        Create a range model.

        Returns:
            Type[BaseRange]: The range model class.
        """
        pass

    @abstractmethod
    def create_select(self) -> Type[BaseSelect]:
        """
        Create a select model.

        Returns:
            Type[BaseSelect]: The select model class.
        """
        pass

