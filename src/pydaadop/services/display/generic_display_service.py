from typing import Type, Dict, Any, List, Union, Optional

from ...models.base.base_mongo_model import BaseMongoModel
from ..base.base_read_service import BaseReadService
from ...queries.base.base_paging import BasePaging
from ...queries.base.base_sort import BaseSort
from ...queries.base.base_list_filter import BaseListFilter


def _normalize_name(cls: type) -> str:
    name = cls.__name__.lower()
    if name.endswith("model"):
        name = name[:-5]
    return name


class GenericDisplayService(BaseReadService[BaseMongoModel]):
    """Generic read-only service that assembles display models from one
    primary model and one or more secondary source models.

    Convenience: `sources` may be a list of model classes or a mapping name->class.
    If `field_map` is omitted the service will attempt to infer simple mappings
    for fields named like `<source>_id` or `<source>_name`.
    """

    def __init__(
        self,
        display_model: Type[BaseMongoModel],
        primary: Union[str, Type[BaseMongoModel]],
        sources: Union[List[Type[BaseMongoModel]], Dict[str, Type[BaseMongoModel]]],
        primary_foreign_keys: Dict[str, str] | None = None,
        field_map: Dict[str, Dict[str, Any]] | None = None,
    ):
        super().__init__(display_model)
        self.display_model = display_model

        # Normalize sources into a name->model dict
        if isinstance(sources, dict):
            src_map = {k: v for k, v in sources.items()}
        else:
            src_map = {_normalize_name(m): m for m in sources}

        # determine primary name
        if isinstance(primary, str):
            primary_name = primary
        else:
            primary_name = _normalize_name(primary)

        if primary_name not in src_map:
            raise ValueError("primary must be one of the provided sources")

        self.primary_name = primary_name
        self.sources = src_map

        # infer primary_foreign_keys if not given: look for attributes on the
        # primary model that reference secondary names (e.g. 'products' for DemoProduct)
        if primary_foreign_keys is None:
            primary_model = self.sources[self.primary_name]
            anns = getattr(primary_model, "__annotations__", {})
            inferred: Dict[str, str] = {}
            for name in self.sources:
                if name == self.primary_name:
                    continue
                # prefer plural like 'products' then singular
                plural = name + "s"
                if plural in anns:
                    inferred[name] = plural
                elif name in anns:
                    inferred[name] = name
            self.primary_foreign_keys = inferred
        else:
            self.primary_foreign_keys = primary_foreign_keys

        # infer field_map for simple patterns if not provided
        if field_map is None:
            anns = getattr(display_model, "__annotations__", {})
            fmap: Dict[str, Dict[str, Any]] = {}
            for fld in anns:
                if fld.endswith("_id"):
                    src = fld[:-3]
                    if src in self.sources:
                        fmap[fld] = {"source": src, "field": "_id"}
                        continue
                if fld.endswith("_name"):
                    src = fld[:-5]
                    if src in self.sources:
                        fmap[fld] = {"source": src, "field": "name"}
                        continue
                # if field exists on primary model, map from primary
                primary_model = self.sources[self.primary_name]
                panns = getattr(primary_model, "__annotations__", {})
                if fld in panns:
                    fmap[fld] = {"source": self.primary_name, "field": fld}
            self.field_map = fmap
        else:
            self.field_map = field_map

        # create a read service for each source model
        self._services: Dict[str, BaseReadService] = {
            name: BaseReadService(model) for name, model in self.sources.items()
        }

    async def list(
        self,
        paging_query: BasePaging = BasePaging(),
        filter_query: Dict[str, Any] | None = None,
        sort_query: Optional[BaseSort] = None,
        search_query: Dict[str, Any] | None = None,
        range_query: Dict[str, Any] | None = None,
        list_filter: BaseListFilter | None = None,
    ) -> List[BaseMongoModel]:
        # update filter_query with list_filter and range_query like BaseReadService
        filter_query = self._update_filter_query(filter_query, list_filter)
        if range_query:
            if not filter_query:
                filter_query = {}
            filter_query.update(range_query)

        # fetch primary items
        primary_service = self._services[self.primary_name]
        primary_items = await primary_service.list(
            paging_query,
            filter_query,
            sort_query,
            search_query,
            range_query,
            list_filter,
        )

        # gather ids to fetch for each non-primary source
        source_id_map: Dict[str, List[Any]] = {}
        for src_name, src_model in self.sources.items():
            if src_name == self.primary_name:
                continue
            key = self.primary_foreign_keys.get(src_name)
            ids: List[Any] = []
            if key:
                for p in primary_items:
                    val = getattr(p, key, None)
                    if val is None:
                        continue
                    if isinstance(val, (list, tuple)):
                        for v in val:
                            if v not in ids:
                                ids.append(v)
                    else:
                        if val not in ids:
                            ids.append(val)
            source_id_map[src_name] = ids

        # fetch source records in batches
        source_records: Dict[str, Dict[Any, Any]] = {}
        for src_name, ids in source_id_map.items():
            if not ids:
                source_records[src_name] = {}
                continue
            svc = self._services[src_name]
            # request by _id in bulk
            items = await svc.list(filter_query={"_id": {"$in": ids}})
            source_records[src_name] = {getattr(i, "id", getattr(i, "_id", None)): i for i in items}

        # assemble display rows
        rows: List[BaseMongoModel] = []
        for p in primary_items:
            # For sources that are lists on primary, build multiple rows per element
            per_primary_lists = {}
            for src_name in self.sources:
                if src_name == self.primary_name:
                    continue
                key = self.primary_foreign_keys.get(src_name)
                if not key:
                    per_primary_lists[src_name] = [None]
                    continue
                val = getattr(p, key, None)
                if val is None:
                    per_primary_lists[src_name] = [None]
                elif isinstance(val, (list, tuple)):
                    per_primary_lists[src_name] = list(val)
                else:
                    per_primary_lists[src_name] = [val]

            # produce cartesian product across secondary lists; for common patterns
            # like 1 primary -> N products we iterate over product ids
            # For simplicity handle single secondary source list expansion if present
            secondary_names = [n for n in self.sources if n != self.primary_name]
            if len(secondary_names) == 1:
                sec = secondary_names[0]
                for sec_id in per_primary_lists.get(sec, [None]):
                    row_data: Dict[str, Any] = {}
                    for fld, mapping in self.field_map.items():
                        if "constant" in mapping:
                            row_data[fld] = mapping["constant"]
                            continue
                        src = mapping.get("source")
                        fld_name = mapping.get("field")
                        if src == self.primary_name:
                            row_data[fld] = getattr(p, fld_name, None)
                        else:
                            # if this is the expanded source, use sec_id to lookup
                            if sec_id is None:
                                row_data[fld] = None
                            else:
                                rec = source_records.get(src, {}).get(sec_id)
                                row_data[fld] = getattr(rec, fld_name, None) if rec is not None else None
                    rows.append(self.display_model(**row_data))
            else:
                # fallback: single row per primary, attempt to map using first element
                row_data: Dict[str, Any] = {}
                for fld, mapping in self.field_map.items():
                    if "constant" in mapping:
                        row_data[fld] = mapping["constant"]
                        continue
                    src = mapping.get("source")
                    fld_name = mapping.get("field")
                    if src == self.primary_name:
                        row_data[fld] = getattr(p, fld_name, None)
                    else:
                        ids = per_primary_lists.get(src, [None])
                        rec = source_records.get(src, {}).get(ids[0]) if ids else None
                        row_data[fld] = getattr(rec, fld_name, None) if rec is not None else None
                rows.append(self.display_model(**row_data))

        return rows

    async def get(self, key_filter_query: Dict[str, Any]):
        # expect keys for primary and optionally secondary ids
        # try to fetch primary first
        primary_svc = self._services[self.primary_name]
        primary = await primary_svc.get(key_filter_query)
        if not primary:
            return None

        # collect secondary ids from primary using primary_foreign_keys
        sec_values = {}
        for src_name in self.sources:
            if src_name == self.primary_name:
                continue
            key = self.primary_foreign_keys.get(src_name)
            if not key:
                sec_values[src_name] = None
            else:
                sec_values[src_name] = getattr(primary, key, None)

        # build row data
        row_data: Dict[str, Any] = {}
        for fld, mapping in self.field_map.items():
            if "constant" in mapping:
                row_data[fld] = mapping["constant"]
                continue
            src = mapping.get("source")
            fld_name = mapping.get("field")
            if src == self.primary_name:
                row_data[fld] = getattr(primary, fld_name, None)
            else:
                sid = key_filter_query.get(f"{src}_id") or (sec_values.get(src)[0] if isinstance(sec_values.get(src), (list, tuple)) and sec_values.get(src) else sec_values.get(src))
                if sid is None:
                    row_data[fld] = None
                else:
                    rec = (await self._services[src].list(filter_query={"_id": sid}))
                    if rec:
                        rec = rec[0]
                    else:
                        rec = None
                    row_data[fld] = getattr(rec, fld_name, None) if rec is not None else None

        return self.display_model(**row_data)
