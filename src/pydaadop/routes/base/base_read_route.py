"""
This module provides the BaseReadRouter class, which sets up routes for reading
MongoDB models.

Classes:
    BaseReadRouter: A router class for reading MongoDB models.
"""

from typing import List, Type, TypeVar
from fastapi import Depends, HTTPException

from ...models.base import BaseMongoModel
from ...models.display import DisplayItemInfo, DisplayQueryInfo
from ...queries.base.base_paging import BasePaging
from ...queries.base.base_query import BaseQuery
from ...queries.base.base_search import BaseSearch
from ...services.base.base_read_service import BaseReadService
from ...services.interface.read_service_interface import ReadServiceInterface
from typing_extensions import override

from .base_route import BaseRouter

T = TypeVar("T", bound=BaseMongoModel)  # Generic type for the model class

class BaseReadRouter(BaseRouter[T]):
    """
    A router class for reading MongoDB models.

    Attributes:
        service (ReadServiceInterface): The service for reading operations.
    """

    def __init__(self, model: Type[T], service: ReadServiceInterface = None):
        """
        Initialize the BaseReadRouter.

        Args:
            model (Type[T]): The MongoDB model type.
            service (ReadServiceInterface, optional): The service for reading operations. Defaults to None.
        """
        self.service = service if service else BaseReadService(model)
        super().__init__(model)

    @override
    def create_openapi_schema(self, schema: dict) -> dict:
        """
        Create the OpenAPI schema for the routes.

        Args:
            schema (dict): The OpenAPI schema.

        Returns:
            dict: The updated OpenAPI schema.
        """
        models = [self.service.create_filter(), self.service.create_key_filter(), self.service.create_range(), self.service.create_sort(),
                  self.service.create_select()]

        # Ensure the components section exists
        if schema.get("components") is None:
            schema["components"] = {}
        if schema["components"].get("schemas") is None:
            schema["components"]["schemas"] = {}

        for model in models:
            dynamic_model_schema = model.model_json_schema()
            dynamic_model_schema["title"] = model.__name__

            # Dynamically add the model schema to OpenAPI
            schema["components"]["schemas"][model.__name__] = dynamic_model_schema

        return schema

    @override
    def setup_routes(self):
        """
        Set up the routes for reading operations.
        """
        super().setup_routes()

        model = self.model  # Store the model locally for static use
        filter_model = self.service.create_filter()
        key_filter_model = self.service.create_key_filter()
        range_model = self.service.create_range()
        sort_model = self.service.create_sort()
        select_model = self.service.create_select()

        @self.router.get(f"{self.prefix}/display-info/query/", response_model=DisplayQueryInfo)
        async def get_display_query_info():
            """
            Get display query information.

            Returns:
                DisplayQueryInfo: The display query information.
            """
            display_info = await self.service.query_info(model=model)
            return display_info

        @self.router.get(f"{self.prefix}/display-info/item/", response_model=DisplayItemInfo)
        async def get_display_item_info(
                filter_query: filter_model = Depends(),
                range_query: range_model = Depends(),
                search_query: BaseSearch = Depends()):
            """
            Get display item information.

            Args:
                filter_query (filter_model, optional): The filter query. Defaults to Depends().
                range_query (range_model, optional): The range query. Defaults to Depends().
                search_query (BaseSearch, optional): The search query. Defaults to Depends().

            Returns:
                DisplayItemInfo: The display item information.
            """
            range_dict = BaseQuery.extract_range(range_query)
            filter_dict = BaseQuery.extract_filter(filter_model=filter_query)
            search_dict = BaseQuery.extract_search(model=model, search_model=search_query)
            display_info = await self.service.item_info(filter_query=filter_dict, range_query=range_dict, search_query=search_dict)
            return display_info

        @self.router.get(f"{self.prefix}/", response_model=List[model])
        async def get_all(
                sort_query: sort_model = Depends(),
                range_query: range_model = Depends(),
                paging_query: BasePaging = Depends(),
                filter_query: filter_model = Depends(),
                search_query: BaseSearch = Depends()):
            """
            Get all items.

            Args:
                sort_query (sort_model, optional): The sort query. Defaults to Depends().
                range_query (range_model, optional): The range query. Defaults to Depends().
                paging_query (BasePaging, optional): The paging query. Defaults to Depends().
                filter_query (filter_model, optional): The filter query. Defaults to Depends().
                search_query (BaseSearch, optional): The search query. Defaults to Depends().

            Returns:
                List[model]: The list of items.
            """
            range_dict = BaseQuery.extract_range(range_query)
            filter_dict = BaseQuery.extract_filter(filter_query)
            search_dict = BaseQuery.extract_search(model, search_query)
            items = await self.service.list(filter_query=filter_dict, sort_query=sort_query, paging_query=paging_query,
                                            range_query=range_dict, search_query=search_dict)
            return items

        @self.router.get(f"{self.prefix}/select/", response_model=List[dict])
        async def get_all_select(
                select_query: select_model = Depends(),
                range_query: range_model = Depends(),
                sort_query: sort_model = Depends(),
                filter_query: filter_model = Depends(),
                search_query: BaseSearch = Depends()):
            """
            Get all items with selected fields.

            Args:
                select_query (select_model, optional): The select query. Defaults to Depends().
                range_query (range_model, optional): The range query. Defaults to Depends().
                sort_query (sort_model, optional): The sort query. Defaults to Depends().
                filter_query (filter_model, optional): The filter query. Defaults to Depends().
                search_query (BaseSearch, optional): The search query. Defaults to Depends().

            Returns:
                List[dict]: The list of items with selected fields.
            """
            keys = [select_query.selected_field]
            range_dict = BaseQuery.extract_range(range_query)
            filter_dict = BaseQuery.extract_filter(filter_query)
            search_dict = BaseQuery.extract_search(model, search_query)
            items = await self.service.list_keys(keys=keys, filter_query=filter_dict, sort_query=sort_query,
                                                 range_query=range_dict, search_query=search_dict)

            # Adjust the _id to be string instead of ObjectId
            for item in items:
                item["_id"] = str(item["_id"])


            return items

        @self.router.get(f"{self.prefix}/exists/", response_model=bool)
        async def item_exists(key_filter_query: key_filter_model = Depends()):
            """
            Check if an item exists.

            Args:
                key_filter_query (key_filter_model, optional): The key filter query. Defaults to Depends().

            Returns:
                bool: True if the item exists, False otherwise.
            """
            key_filter_dict = BaseQuery.extract_filter(key_filter_query)
            return await self.service.exists(key_filter_dict)


        @self.router.get(f"{self.prefix}/item/", response_model=model)
        async def get_item(key_filter_query: key_filter_model = Depends()):
            """
            Get an item.

            Args:
                key_filter_query (key_filter_model, optional): The key filter query. Defaults to Depends().

            Returns:
                model: The item.

            Raises:
                HTTPException: If the item is not found.
            """
            key_filter_dict = BaseQuery.extract_filter(key_filter_query)
            item = await self.service.get(key_filter_dict)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item

