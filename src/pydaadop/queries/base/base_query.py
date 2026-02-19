# Create a type variable for the model
from enum import Enum
from typing import TypeVar, Type, Optional, Any, Dict, get_type_hints, List, Tuple, get_origin, get_args, Literal

from bson import ObjectId
from fastapi import Query
from pydantic import create_model, BaseModel

from .base_range import BaseRange
from .base_search import BaseSearch
from .base_select import BaseSelect
from ...models.base import BaseMongoModel
from ...models.display.display_query_info import DisplayFilterInfo, DisplayFilterAttributeInfo, DisplaySortInfo, \
    DisplaySortAttributeInfo, DisplayQueryInfo
from ...queries.base.base_sort import BaseSort

class BaseQuery:
    """
    BaseQuery class for creating and managing query models.

    Attributes:
        supported_types (list): List of supported types for queries.
        supported_selectable_types (list): List of supported selectable types for queries.
    """
    supported_types = [str, int, float]
    supported_selectable_types = [bool]

    @classmethod
    def _get_type(cls, annotation: Any) -> Tuple[type | None, bool]:
        """
        Get the type of the annotation.

        Args:
            annotation (Any): The annotation to get the type of.

        Returns:
            Tuple[type | None, bool]: The type and whether it is selectable.
        """
        if not annotation:
            return None, False

        origin = get_origin(annotation) or annotation
        args = get_args(annotation)

        # Check if it's a basic type directly or an Optional wrapping a basic type
        if origin in cls.supported_types:
            return origin, False
        if args and (args[0] in cls.supported_types):
            return args[0], False

        # Handle Literal types by extracting the type of its values
        if origin == Literal:
            literal_type = type(args[0]) if args else None
            if literal_type in cls.supported_types:
                return literal_type, True
            return None, False

        # Guard issubclass check: origin may be a typing construct (not a class)
        if isinstance(origin, type) and issubclass(origin, Enum):
            return str, True

        # Recursively check nested types if no valid type is found
        if args and origin is not None:
            return cls._get_type(args[0])

        return None, False

    @classmethod
    def _is_supported_type(cls, field_type: type, is_selectable: bool, name: str, only_selectable: True) -> bool:
        """
        Check if the field type is supported.

        Args:
            field_type (type): The field type to check.
            is_selectable (bool): Whether the field is selectable.
            name (str): The name of the field.
            only_selectable (bool): Whether to only check selectable fields.

        Returns:
            bool: True if the field type is supported, False otherwise.
        """
        if not only_selectable:
            return True

        if name.endswith("_id") or is_selectable or field_type in cls.supported_selectable_types:
            return True

        return False

    @classmethod
    def _get_allowed_values(cls, annotation: Any) -> list | None:
        """
        Extract allowed values if the annotation is a Literal.

        Args:
            annotation (Any): The annotation to extract allowed values from.

        Returns:
            list | None: The list of allowed values or None.
        """
        if get_origin(annotation) == Literal:
            return list(get_args(annotation))

        args = get_args(annotation)

        if args and args[0]:
            return cls._get_allowed_values(args[0])

        return None

    @classmethod
    def get_fields_of_model(cls, model: Type[BaseModel], only_selectable=True) -> Dict[str, Any]:
        """
        Get the fields of the model.

        Args:
            model (Type[BaseModel]): The model to get the fields of.
            only_selectable (bool): Whether to only get selectable fields.

        Returns:
            Dict[str, Any]: The dictionary of fields.
        """
        all_fields: Dict[str, Any] = {}
        field_overrides = {}

        # Collect fields and their annotations, skipping custom classes
        model_fields = get_type_hints(model)
        for name, annotation in model_fields.items():
            # Only add fields that are basic types
            field_type, selectable = cls._get_type(annotation)
            if cls._is_supported_type(field_type, selectable, name, only_selectable):
                if name in all_fields:
                    all_fields[name].append(annotation)
                else:
                    all_fields[name] = [annotation]

        # Process the fields to set as optional in the combined model
        for name, annotations in all_fields.items():
            base_annotation = annotations[0]

            # Ensure all annotations are identical
            for annotation in annotations:
                assert annotation == base_annotation, f"{name} has different types in the models"

            # Make the field optional and add to field overrides
            field_overrides[name] = (Optional[base_annotation], Query(None))

        return field_overrides

    @classmethod
    def create_filter(cls, models: list[Type[BaseModel]], only_selectable=True) -> Type[BaseModel]:
        """
        Create a filter model for the given models.

        Args:
            models (list[Type[BaseModel]]): The list of models to create the filter for.
            only_selectable (bool): Whether to only create selectable fields.

        Returns:
            Type[BaseModel]: The created filter model.
        """
        field_overrides = {}
        name = ""
        for model in models:
            name += model.__name__
            field_overrides.update(cls.get_fields_of_model(model, only_selectable))

        # Create a new model dynamically with the combined optional fields
        query_model = create_model(f"{name}FilterModel", **field_overrides)
        return query_model

    @classmethod
    def create_key_filter(cls, models: list[Type[BaseModel]]) -> Type[BaseModel]:
        """
        Create a key filter model for the given models.

        Args:
            models (list[Type[BaseModel]]): The list of models to create the key filter for.

        Returns:
            Type[BaseModel]: The created key filter model.
        """
        field_overrides = {}
        name = ""
        for model in models:
            name += model.__name__
            field_names = model.create_index()
            fields = cls.get_fields_of_model(model, False)

            for key in fields:
                if key in field_names:
                    field_overrides[key] = fields[key]

        # Create a new model dynamically with the combined optional fields
        query_model = create_model(f"{name}KeyFilterModel", **field_overrides)
        return query_model

    @classmethod
    def split_filter(cls, models: list[Type[BaseModel]], filter_data: Dict) -> List[Dict]:
        """
        Split the filter data into the different models based on the keys which represent the model fields.

        Args:
            models ([Type[BaseModel]]): The list of models to split the filter data for.
            filter_data (Dict): The filter data to split.

        Returns:
            List[Dict]: The list of split filter data.
        """
        # split the filter data into the different models based on the keys which represent the model fields
        split_filter_data = [{} for _ in range(len(models))]

        for key, value in filter_data.items():
            for i, model in enumerate(models):
                if key in get_type_hints(model):
                    split_filter_data[i][key] = value
                    break

        return split_filter_data

    @classmethod
    def split_sort(cls, models: list[Type[BaseModel]], sort_model: BaseSort) -> List[BaseSort | None]:
        """
        Split the sort model into the different models based on the sort_by field.

        Args:
            models ([Type[BaseModel]]): The list of models to split the sort model for.
            sort_model (BaseSort): The sort model to split.

        Returns:
            List[BaseSort | None]: The list of split sort models.
        """
        # check if the sort model has a sort_by field
        if not sort_model.sort_by:
            return [None for _ in range(len(models))]

        # the sort by field is in one of the models
        sort_by = sort_model.sort_by

        # find the first model that has the sort_by field
        for i, model in enumerate(models):
            if sort_by in get_type_hints(model):
                return [BaseSort(sort_by=sort_by, sort_order=sort_model.sort_order) if j == i else None for j in range(len(models))]


    @classmethod
    def extract_filter(cls, filter_model: BaseModel, exclude=True) -> dict:
        """
        Extract the filter data from the filter model.

        Args:
            filter_model (BaseModel): The filter model to extract the data from.
            exclude (bool): Whether to exclude None, unset, and default values.

        Returns:
            dict: The extracted filter data.
        """
        filter_data = filter_model.model_dump(exclude_none=exclude, exclude_unset=exclude, exclude_defaults=exclude)

        if "id" in filter_data:
            filter_data["_id"] = filter_data.pop("id")

        return filter_data

    @classmethod
    def extract_range(cls, range_model: BaseRange) -> dict:
        """
        Extract the range data from the range model.

        Args:
            range_model (BaseRange): The range model to extract the data from.

        Returns:
            dict: The extracted range data.
        """
        if not range_model.range_by or not (range_model.gte_value or range_model.lte_value):
            return {}

        range_dict = {range_model.range_by: {}}
        if range_model.gte_value:
            range_dict[range_model.range_by]["$gte"] = int(
                range_model.gte_value) if range_model.gte_value.isdigit() else range_model.gte_value
        if range_model.lte_value:
            range_dict[range_model.range_by]["$lte"] = int(
                range_model.lte_value) if range_model.lte_value.isdigit() else range_model.lte_value

        return range_dict

    @classmethod
    def create_sort(cls, models: list[Type[BaseModel]]) -> Type[BaseSort]:
        """
        Create a sort model for the given models.

        Args:
            models (list[Type[BaseModel]]): The list of models to create the sort model for.

        Returns:
            Type[BaseSort]: The created sort model.
        """
        model_name = "_".join([model.__name__ for model in models])
        filter_model = cls.create_filter(models, only_selectable=False)
        filterable_fields = cls.extract_filter(filter_model(), exclude=False)
        # only take the keys
        filterable_fields_names = [str(key) for key in filterable_fields.keys()]

        if not filterable_fields_names or len(filterable_fields_names) == 0:
            return BaseSort

        # sort_by_literal = Literal[*filterable_fields_names]
        sort_by_literal = Literal.__getitem__(tuple(filterable_fields_names))

        # now we create a sort model for the model
        class CustomSort(BaseSort):
            # Dynamically define the sort_by field based on filterable_fields
            sort_by: Optional[sort_by_literal] = Query(
                default=None,
                description="Field to sort by"
            )

        return create_model(
            f"{model_name}Sort",  # Set the name dynamically
            __base__=CustomSort  # Inherit from BaseRange
        )
    @classmethod
    def create_range(cls, models: list[Type[BaseModel]]) -> Type[BaseRange]:
        """
        Create a range model for the given models.

        Args:
            models (list[Type[BaseModel]]): The list of models to create the range model for.

        Returns:
            Type[BaseRange]: The created range model.
        """
        model_name = "_".join([model.__name__ for model in models])
        filter_model = cls.create_filter(models, only_selectable=False)
        filterable_fields = cls.extract_filter(filter_model(), exclude=False)
        # only take the keys
        filterable_fields_names = [str(key) for key in filterable_fields.keys()]

        if not filterable_fields_names or len(filterable_fields_names) == 0:
            return BaseRange

        # sort_by_literal = Literal[*filterable_fields_names]
        sort_by_literal = Literal.__getitem__(tuple(filterable_fields_names))

        # now we create a sort model for the model
        class CustomRange(BaseRange):
            # Dynamically define the sort_by field based on filterable_fields
            range_by: Optional[sort_by_literal] = Query(
                default=None,
                description="Field to slect range by"
            )
            __name__ = f"{model_name}Range"

        return create_model(
            f"{model_name}Range",  # Set the name dynamically
            __base__=CustomRange  # Inherit from BaseRange
        )


    @classmethod
    def create_select(cls, models: list[Type[BaseModel]]) -> Type[BaseSelect]:
        """
        Create a select model for the given models.

        Args:
            models (list[Type[BaseModel]]): The list of models to create the select model for.

        Returns:
            Type[BaseSelect]: The created select model.
        """
        model_name = "_".join([model.__name__ for model in models])
        # get all the fields of the models and create a boolean field for each field
        selectable_fields = {}
        for model in models:
            model_fields = get_type_hints(model)
            for name, annotation in model_fields.items():
                field_type, _ = cls._get_type(annotation)
                selectable_fields[name] = name

        if not selectable_fields:
            return BaseSelect

        # create the selectable fields (each field is a boolean)
        selectable_fields_literal = Literal.__getitem__(tuple(selectable_fields.keys()))

        class CustomSelect(BaseSelect):
            # Dynamically define the select field based on selectable_fields
            selected_field: Optional[selectable_fields_literal] = Query(
                default=None,
                description="Field to select"
            )

        return create_model(
            f"{model_name}Select",  # Set the name dynamically
            __base__=CustomSelect  # Inherit from BaseRange
        )


    @classmethod
    def extract_search(cls, model: Type[BaseModel], search_model: BaseSearch) -> Dict:
        """
        Extract the search query from the search model.

        Args:
            model (Type[BaseModel]): The model to extract the search query for.
            search_model (BaseSearch): The search model to extract the query from.

        Returns:
            Dict: The extracted search query.
        """
        if not search_model.search:
            return {}
        filter_model = cls.create_filter([model], only_selectable=False)
        searchable_fields = cls.extract_filter(filter_model(), exclude=False)
        # only take the keys
        searchable_field_names = [str(key) for key in searchable_fields.keys()]

        search_query = {
            "$or": [
                {field: {"$regex": search_model.search, "$options": "i"}} for field in searchable_field_names
            ]
        }

        return search_query

    @classmethod
    def create_display_filter_info(cls, model: Type[BaseModel]) -> DisplayFilterInfo:
        """
        Create display filter info for the given model.

        Args:
            model (Type[BaseModel]): The model to create the display filter info for.

        Returns:
            DisplayFilterInfo: The created display filter info.
        """
        filter_model = cls.create_filter([model], only_selectable=True)

        model_fields = get_type_hints(filter_model)

        filter_attributes = []

        for name, annotation in model_fields.items():
            field_type, _ = cls._get_type(annotation)
            if not field_type:
                continue

            allowed_values = cls._get_allowed_values(annotation)

            # Create the filter attribute info
            filter_attribute = DisplayFilterAttributeInfo(
                name=name,
                type=field_type.__name__,
                allowed_values=allowed_values,
                parent=model.__name__
            )
            filter_attributes.append(filter_attribute)

        return DisplayFilterInfo(filter_attributes=filter_attributes)

    @classmethod
    def combine_display_filter_info(cls, info_filters: list[DisplayFilterInfo]) -> DisplayFilterInfo:
        """
        Combine multiple display filter info objects into one.

        Args:
            info_filters (list[DisplayFilterInfo]): The list of display filter info objects to combine.

        Returns:
            DisplayFilterInfo: The combined display filter info.
        """
        combined_filter_info = None

        for info_filter in info_filters:
            if not combined_filter_info:
                combined_filter_info = info_filter
                continue
            combined_filter_info.filter_attributes.extend(info_filter.filter_attributes)

        return combined_filter_info

    @classmethod
    def combine_display_sort_info(cls, info_sorts: list[DisplaySortInfo]) -> DisplaySortInfo:
        """
        Combine multiple display sort info objects into one.

        Args:
            info_sorts (list[DisplaySortInfo]): The list of display sort info objects to combine.

        Returns:
            DisplaySortInfo: The combined display sort info.
        """
        combined_sort_info = None

        for info_sort in info_sorts:
            if not combined_sort_info:
                combined_sort_info = info_sort
                continue
            combined_sort_info.sort_attributes.extend(info_sort.sort_attributes)

        return combined_sort_info

    @classmethod
    def combine_display_query_info(cls, info_queries: list[DisplayQueryInfo]) -> DisplayQueryInfo:
        """
        Combine multiple display query info objects into one.

        Args:
            info_queries (list[DisplayQueryInfo]): The list of display query info objects to combine.

        Returns:
            DisplayQueryInfo: The combined display query info.
        """
        combined_query_info = DisplayQueryInfo(
            filter_info=cls.combine_display_filter_info([info_query.filter_info for info_query in info_queries]),
            sort_info=cls.combine_display_sort_info([info_query.sort_info for info_query in info_queries])
        )
        return combined_query_info

    @classmethod
    def create_display_sort_info(cls, model: Type[BaseModel]) -> DisplaySortInfo:
        """
        Create display sort info for the given model.

        Args:
            model (Type[BaseModel]): The model to create the display sort info for.

        Returns:
            DisplaySortInfo: The created display sort info.
        """
        filter_model = cls.create_filter([model], only_selectable=False)
        filterable_fields = cls.extract_filter(filter_model(), exclude=False)
        # only take the keys
        filterable_fields_names = [DisplaySortAttributeInfo(name=str(key), parent=model.__name__) for key in filterable_fields.keys()]

        return DisplaySortInfo(sort_attributes=filterable_fields_names)







