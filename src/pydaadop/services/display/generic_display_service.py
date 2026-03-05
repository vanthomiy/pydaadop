from abc import abstractmethod
from typing import TypeVar, Generic, Type, Dict, Any, List, Optional, Callable
from typing import Unpack, TypeVarTuple

from ...models.base.base_mongo_model import BaseMongoModel
from ..base.base_read_service import BaseReadService
from ...queries.base.base_paging import BasePaging
from ...queries.base.base_sort import BaseSort
from ...queries.base.base_list_filter import BaseListFilter

D = TypeVar("D", bound=BaseMongoModel)
Sources = TypeVarTuple("Sources")


def _normalize_name(cls: type) -> str:
    name = cls.__name__.lower()
    if name.endswith("model"):
        name = name[:-5]
    return name


class GenericDisplayService(Generic[D, Unpack[Sources]]):
    """
    Generic read-only display service.

    Type parameters:
        D          – the display/output model
        *Sources   – source models in order; the FIRST is the primary

    Usage:
        class MyService(GenericDisplayService[MyDisplay, Buyer, Product, Payment]):
            def mapping(self, primary: Buyer, sources: dict) -> MyDisplay:
                product = sources["product"]
                payment = sources["payment"]
                return MyDisplay(...)

    The `mapping()` method receives:
        - primary:  first source model instance
        - sources:  dict[normalized_class_name, instance] for all other sources
    """

    def __init__(
        self,
        display_model: Type[D],
        *source_models: Type[BaseMongoModel],
        primary_foreign_keys: Optional[Dict[str, str]] = None,
        field_map: Optional[Dict[str, Dict[str, Any]]] = None,
        mapping: Optional[Callable] = None,
    ):
        if not source_models:
            raise ValueError("Provide at least one source model (the primary).")

        self.display_model = display_model
        primary_model = source_models[0]
        self.primary_name = _normalize_name(primary_model)

        self.sources: Dict[str, Type[BaseMongoModel]] = {
            _normalize_name(m): m for m in source_models
        }

        # ── primary_foreign_keys ──────────────────────────────────────────────
        if primary_foreign_keys is None:
            anns = getattr(primary_model, "__annotations__", {})
            inferred: Dict[str, str] = {}
            for name in self.sources:
                if name == self.primary_name:
                    continue
                plural = name + "s"
                if plural in anns:
                    inferred[name] = plural
                elif name in anns:
                    inferred[name] = name
            self.primary_foreign_keys = inferred
        else:
            self.primary_foreign_keys = primary_foreign_keys

        # ── field_map ─────────────────────────────────────────────────────────
        if field_map is None:
            display_anns  = getattr(display_model,  "__annotations__", {})
            primary_anns  = getattr(primary_model,  "__annotations__", {})
            fmap: Dict[str, Dict[str, Any]] = {}
            for fld in display_anns:
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
                if fld in primary_anns:
                    fmap[fld] = {"source": self.primary_name, "field": fld}
            self.field_map = fmap
        else:
            self.field_map = field_map

        # ── one BaseReadService per source ────────────────────────────────────
        self._services: Dict[str, BaseReadService] = {
            name: BaseReadService(model) for name, model in self.sources.items()
        }

        self._mapping_override: Optional[Callable] = mapping

    # ─────────────────────────────────────────────────────────────────────────
    # Mapping hook
    # ─────────────────────────────────────────────────────────────────────────
    @abstractmethod
    def mapping(
        self,
        primary: BaseMongoModel,
        sources: Dict[str, Optional[BaseMongoModel]],
    ) -> D:
        raise NotImplementedError(
            "Override mapping() in your subclass or pass mapping= to __init__."
        )

    def _resolve_mapping(self) -> Optional[Callable]:
        if self._mapping_override is not None:
            return self._mapping_override
        if type(self).mapping is not GenericDisplayService.mapping:
            return self.mapping
        return None  # fall back to field_map

    def _build_row_data(
        self,
        primary: BaseMongoModel,
        source_recs: Dict[str, Optional[BaseMongoModel]],
    ) -> Dict[str, Any]:
        row: Dict[str, Any] = {}
        for fld, cfg in self.field_map.items():
            if "constant" in cfg:
                row[fld] = cfg["constant"]
                continue
            src  = cfg["source"]
            attr = cfg["field"]
            if src == self.primary_name:
                row[fld] = getattr(primary, attr)
            else:
                rec = source_recs.get(src)
                row[fld] = getattr(rec, attr) if rec is not None else None
        return row

    def _apply_mapping(
        self,
        primary: BaseMongoModel,
        source_recs: Dict[str, Optional[BaseMongoModel]],
    ) -> D:
        fn = self._resolve_mapping()
        if fn is not None:
            return fn(primary, source_recs)
        return self.display_model(**self._build_row_data(primary, source_recs))

    # ─────────────────────────────────────────────────────────────────────────
    # list
    # ─────────────────────────────────────────────────────────────────────────

    async def list(
        self,
        paging_query: BasePaging = BasePaging(),
        filter_query: Optional[Dict[str, Any]] = None,
        sort_query: Optional[BaseSort] = None,
        search_query: Optional[Dict[str, Any]] = None,
        range_query: Optional[Dict[str, Any]] = None,
        list_filter: Optional[BaseListFilter] = None,
    ) -> List[D]:
        if range_query:
            filter_query = {**(filter_query or {}), **range_query}

        primary_items: List[BaseMongoModel] = await self._services[self.primary_name].list(
            paging_query, filter_query, sort_query, search_query, range_query, list_filter
        )

        secondary_names = [n for n in self.sources if n != self.primary_name]

        # ── collect FK ids ────────────────────────────────────────────────────
        source_id_map: Dict[str, List[Any]] = {n: [] for n in secondary_names}
        for src_name in secondary_names:
            key = self.primary_foreign_keys.get(src_name)
            if not key:
                continue
            seen: List[Any] = []
            for p in primary_items:
                val = getattr(p, key, None)
                if val is None:
                    continue
                for v in (list(val) if isinstance(val, (list, tuple)) else [val]):
                    if v not in seen:
                        seen.append(v)
            source_id_map[src_name] = seen

        # ── bulk-fetch secondaries ────────────────────────────────────────────
        source_records: Dict[str, Dict[Any, BaseMongoModel]] = {}
        for src_name, ids in source_id_map.items():
            if not ids:
                source_records[src_name] = {}
                continue
            items = await self._services[src_name].list(filter_query={"_id": {"$in": ids}})
            source_records[src_name] = {
                (i.id if hasattr(i, "id") else i._id): i for i in items
            }

        # ── assemble rows ─────────────────────────────────────────────────────
        rows: List[D] = []
        for p in primary_items:
            per_lists: Dict[str, List[Any]] = {}
            for src_name in secondary_names:
                key = self.primary_foreign_keys.get(src_name)
                val = getattr(p, key, None) if key else None
                if val is None:
                    per_lists[src_name] = [None]
                elif isinstance(val, (list, tuple)):
                    per_lists[src_name] = list(val)
                else:
                    per_lists[src_name] = [val]

            if len(secondary_names) == 1:
                sec = secondary_names[0]
                for sec_id in per_lists[sec]:
                    rec = source_records.get(sec, {}).get(sec_id) if sec_id is not None else None
                    rows.append(self._apply_mapping(p, {sec: rec}))
            else:
                source_recs: Dict[str, Optional[BaseMongoModel]] = {
                    src_name: (
                        source_records.get(src_name, {}).get(per_lists[src_name][0])
                        if per_lists[src_name][0] is not None else None
                    )
                    for src_name in secondary_names
                }
                rows.append(self._apply_mapping(p, source_recs))

        return rows

    # ─────────────────────────────────────────────────────────────────────────
    # get
    # ─────────────────────────────────────────────────────────────────────────

    async def get(self, key_filter_query: Dict[str, Any]) -> Optional[D]:
        primary = await self._services[self.primary_name].get(key_filter_query)
        if not primary:
            return None

        secondary_names = [n for n in self.sources if n != self.primary_name]
        source_recs: Dict[str, Optional[BaseMongoModel]] = {}

        for src_name in secondary_names:
            key = self.primary_foreign_keys.get(src_name)
            sid = key_filter_query.get(f"{src_name}_id")
            if sid is None and key:
                raw = getattr(primary, key, None)
                sid = raw[0] if isinstance(raw, (list, tuple)) and raw else raw
            if sid is None:
                source_recs[src_name] = None
            else:
                results = await self._services[src_name].list(filter_query={"_id": sid})
                source_recs[src_name] = results[0] if results else None

        return self._apply_mapping(primary, source_recs)