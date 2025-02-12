from abc import ABC
from typing import List, Optional, Dict, Type

from ...services.interface.service_interface import ServiceInterface

from ...models.base.base_mongo_model import BaseMongoModel
from pydantic import BaseModel

from ..base.base_read_service import BaseReadService
from ...queries.base.base_list_filter import BaseListFilter
from ...queries.base.base_paging import BasePaging
from ...queries.base.base_query import BaseQuery
from ...queries.base.base_sort import BaseSort


class DisplayService(ServiceInterface[BaseMongoModel], ABC):
    def __init__(self, model: Type[BaseMongoModel]):
        """
        Initialize the DisplayService with a specific model.

        Args:
            model (Type[BaseMongoModel]): The model type to be used by the service.
        """
        super().__init__(model)

    @classmethod
    async def _apply_primary_filter(
                   cls,
                   models: List[Type[BaseModel]],
                   services: List[BaseReadService[BaseModel]],
                   foreign_ids: list[str],
                   filter_query: Dict = None,
                   search_query: Dict = None) -> dict | None:
        """
        Apply the primary filter to the list of models and services based on the provided foreign IDs and queries.

        Args:
            models (List[Type[BaseModel]]): List of model types.
            services (List[BaseReadService[BaseModel]]): List of services corresponding to the models.
            foreign_ids (list[str]): List of foreign ID fields.
            filter_query (Dict, optional): Dictionary containing filter criteria.
            search_query (Dict, optional): Dictionary containing search criteria.

        Returns:
            dict | None: A dictionary representing the primary filter or None if the input is invalid.
        """
        # check if basic query is valid
        if not models or not services or not foreign_ids:
            return None
        if len(models) != len(services) or len(models) != len(foreign_ids):
            return None

        filters = BaseQuery.split_filter(models, filter_query)

        foreign_ids_items = await services[0].list_keys(foreign_ids, filter_query=filters[0])
        # instead of list of dict items we want to transform to dict of lists
        foreign_ids_dict = {key: [item[key] for item in foreign_ids_items] for key in foreign_ids}

        ids = {}

        # key forward pass
        for i in range(1, len(models)):
            list_filter = BaseListFilter(
                key="_id",
                value=foreign_ids_dict[foreign_ids[i]])

            filters[i] = cls._update_filter_query(filters[i], list_filter)
            items = await services[i].list_keys([foreign_ids[0]], filter_query=filters[i])
            ids[i] = [item[foreign_ids[0]] for item in items]

        # key backward pass
        for i in range(1, len(models)):
            list_filter = BaseListFilter(
                key=foreign_ids[i],
                value=ids[i])
            filters[0] = cls._update_filter_query(filters[0], list_filter)

        # if search query is present and any key is present, apply search filter
        base_filter = await cls._apply_search_filter(services, foreign_ids, filters, search_query)

        # get primary filter
        return base_filter

    @staticmethod
    async def _apply_search_filter(
                   services: List[BaseReadService[BaseModel]],
                   foreign_ids: list[str],
                   filters: list[dict],
                   search_query: Dict = None) -> dict | None:
        """
        Apply the search filter to the list of services based on the provided search query.

        Args:
            services (List[BaseReadService[BaseModel]]): List of services.
            foreign_ids (list[str]): List of foreign ID fields.
            filters (list[dict]): List of filter dictionaries.
            search_query (Dict, optional): Dictionary containing search criteria.

        Returns:
            dict | None: A dictionary representing the search filter or None if no matching items are found.
        """
        if not search_query or not any(search_query.values()):
            return filters[0]

        base_filter = filters[0]
        matching_idx = None

        for i in range(len(services)):
            if matching_idx:
                break

            info = await services[i].item_info(filter_query=filters[i].copy(), search_query=search_query)
            if info.items_count > 0:
                matching_idx = i
                # if the base filter object we just add the search query to the filter
                if i == 0:
                    base_filter.update(search_query)
                else:
                    # we neet to get all valid ids for the model and update the base filter
                    items = await services[i].list_keys(["_id"] ,filter_query=filters[i], search_query=search_query)
                    list_filter = BaseListFilter(
                        key=foreign_ids[i],
                        value=[item["_id"] for item in items]
                    )
                    base_filter.update(list_filter.to_mongo_filter())

        if not matching_idx:
            return None

        # get primary filter
        return base_filter

    @classmethod
    async def _get_values(
                   cls,
                   models: List[Type[BaseModel]],
                   services: List[BaseReadService[BaseModel]],
                   foreign_ids: list[str],
                   paging_query: BasePaging = BasePaging(),
                   filter_query: Dict = None,
                   sort_query: Optional[BaseSort] = None,
                   search_query: Dict = None) -> List[List[BaseModel]]:
        """
        Retrieve values from the list of models and services based on the provided queries and paging information.

        Args:
            models (List[Type[BaseModel]]): List of model types.
            services (List[BaseReadService[BaseModel]]): List of services corresponding to the models.
            foreign_ids (list[str]): List of foreign ID fields.
            paging_query (BasePaging, optional): Paging information for the query.
            filter_query (Dict, optional): Dictionary containing filter criteria.
            sort_query (Optional[BaseSort], optional): Optional sorting criteria.
            search_query (Dict, optional): Dictionary containing search criteria.

        Returns:
            List[List[BaseModel]]: A list of lists containing the retrieved models.
        """
        base_filter = await cls._apply_primary_filter(
            models=models,
            services=services,
            foreign_ids=foreign_ids,
            filter_query=filter_query,
            search_query=search_query)
        if not base_filter:
            return []

        sort = BaseQuery.split_sort(models, sort_query)

        # final results by model and result id
        result = [
            await services[0].list(paging_query=paging_query, filter_query=base_filter, sort_query=sort[0])]

        for i in range(1, len(models)):
            temp_filter = BaseListFilter(
                key=foreign_ids[0],
                value=[item.__dict__[foreign_ids[i]] for item in result[0]])
            result.append(await services[i].list(paging_query=paging_query, filter_query=temp_filter.to_mongo_filter(), sort_query=sort[i]))

        return result






