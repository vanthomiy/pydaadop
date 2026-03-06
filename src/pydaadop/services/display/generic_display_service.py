from typing import TypeVar, Generic, Type, Dict, Any, List, Optional, Callable
from typing import Unpack, TypeVarTuple

from ...models.base.base_mongo_model import BaseMongoModel
from ...models.display.display_base_model import DisplayBaseModel, _normalize_name
from ..base.base_read_service import BaseReadService
from ...queries.base.base_paging import BasePaging
from ...queries.base.base_sort import BaseSort
from ...queries.base.base_list_filter import BaseListFilter

D = TypeVar("D", bound=DisplayBaseModel)   # ← bound to DisplayBaseModel, not BaseMongoModel
Sources = TypeVarTuple("Sources")

SourceFilters = Dict[str, Dict[str, Any]]


class GenericDisplayService(BaseReadService[D], Generic[D, Unpack[Sources]]):
    """
    Generic read-only display service.

    Expects D to be a DisplayBaseModel subclass — all configuration
    (sources, source_field_map, indexes) is read from it directly.

    Row construction is handled by D.build(primary, sources_dict).
    Override build() on the display model itself for custom logic.

    Subclasses only need to implement search_mapping() if display-level
    filter routing beyond field_map inference is required.

    Minimal usage:
        class MyService(GenericDisplayService[MyDisplay, Payment, Buyer, Product]):
            pass   # everything driven by MyDisplay declarations

    With custom search routing:
        class MyService(GenericDisplayService[MyDisplay, Payment, Buyer, Product]):
            def search_mapping(self, display_filters) -> SourceFilters:
                ...
    """

    def __init__(
        self,
        display_model: Type[D],
        *source_models: Type[BaseMongoModel],
        primary_foreign_keys: Optional[Dict[str, str]] = None,
        search_mapping: Optional[Callable[[Dict[str, Any]], SourceFilters]] = None,
    ):
        if not issubclass(display_model, DisplayBaseModel):
            raise TypeError(
                f"{display_model.__name__} must be a DisplayBaseModel subclass. "
                f"Declare sources, source_field_map, and indexes on it."
            )

        super().__init__(display_model)
        self.display_model = display_model

        # ── Resolve source models ─────────────────────────────────────────────
        resolved = source_models if source_models else tuple(display_model.sources)
        if not resolved:
            raise ValueError(f"No source models found on {display_model.__name__}.sources.")

        primary_model = resolved[0]
        self.primary_name = _normalize_name(primary_model)
        self.sources: Dict[str, Type[BaseMongoModel]] = {
            _normalize_name(m): m for m in resolved
        }

        # ── primary_foreign_keys ──────────────────────────────────────────────
        if primary_foreign_keys is not None:
            self.primary_foreign_keys = primary_foreign_keys
        else:
            # Derive from source_field_map: find primary-side fields that act as FKs
            primary_anns = getattr(primary_model, "__annotations__", {})
            inferred: Dict[str, str] = {}
            for src_name in self.sources:
                if src_name == self.primary_name:
                    continue
                # Look for a primary field explicitly named <src_name>_id
                candidate = f"{src_name}_id"
                if candidate in primary_anns:
                    inferred[src_name] = candidate
                    continue
                # Or a field matching the source name (scalar FK)
                if src_name in primary_anns:
                    inferred[src_name] = src_name
                    continue
                # Or plural
                plural = src_name + "s"
                if plural in primary_anns:
                    inferred[src_name] = plural
            self.primary_foreign_keys = inferred

        # ── reverse_field_map: display_field → (source_name, source_field) ───
        self._reverse_field_map: Dict[str, tuple[str, str]] = {
            display_field: (src_name, src_field)
            for display_field, (src_name, src_field) in display_model.source_field_map.items()
        }

        # ── one BaseReadService per source ────────────────────────────────────
        self._services: Dict[str, BaseReadService] = {
            name: BaseReadService(model) for name, model in self.sources.items()
        }

        # Auto-create indexes
        for svc in self._services.values():
            try:
                svc.create_index()
            except Exception:
                pass

        self._search_mapping_override = search_mapping

    # ─────────────────────────────────────────────────────────────────────────
    # Search mapping hook  (display filters → per-source filters)
    # ─────────────────────────────────────────────────────────────────────────

    def search_mapping(self, display_filters: Dict[str, Any]) -> SourceFilters:
        """
        Override to explicitly route display-level filter keys to source fields.
        Default returns {} — auto-resolved entirely via reverse_field_map.
        """
        return {}

    def _decompose_filter(self, display_filters: Dict[str, Any]) -> SourceFilters:
        fn = self._search_mapping_override or self.search_mapping
        result: SourceFilters = {name: {} for name in self.sources}

        explicit = fn(display_filters)
        for src_name, filters in explicit.items():
            if src_name in result:
                result[src_name].update(filters)

        covered = {f for sf in explicit.values() for f in sf}
        for display_fld, val in display_filters.items():
            if display_fld in self._reverse_field_map:
                src_name, src_field = self._reverse_field_map[display_fld]
                if src_field not in covered:
                    result[src_name][src_field] = val

        return {k: v for k, v in result.items() if v}

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

        primary_filter: Dict[str, Any] = {}
        source_filters: SourceFilters = {}

        if filter_query:
            decomposed = self._decompose_filter(filter_query)
            for src_name, filters in decomposed.items():
                if src_name == self.primary_name:
                    primary_filter.update(filters)
                else:
                    source_filters[src_name] = filters
            for fld, val in filter_query.items():
                if fld not in self._reverse_field_map:
                    primary_filter[fld] = val

        # Pre-filter secondaries → inject FK constraints on primary
        for src_name, filters in source_filters.items():
            matched = await self._services[src_name].list(filter_query=filters)
            ids = [(i.id if hasattr(i, "id") else i._id) for i in matched]
            fk_field = self.primary_foreign_keys.get(src_name)
            if fk_field:
                primary_filter[fk_field] = {"$in": ids}

        primary_items: List[BaseMongoModel] = await self._services[self.primary_name].list(
            paging_query, primary_filter or None, sort_query, search_query, None, list_filter,
        )

        secondary_names = [n for n in self.sources if n != self.primary_name]

        # Collect FK ids from primary rows
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

        # Bulk-fetch secondaries
        source_records: Dict[str, Dict[Any, BaseMongoModel]] = {}
        for src_name, ids in source_id_map.items():
            if not ids:
                source_records[src_name] = {}
                continue
            items = await self._services[src_name].list(filter_query={"_id": {"$in": ids}})
            source_records[src_name] = {
                (i.id if hasattr(i, "id") else i._id): i for i in items
            }

        # Assemble rows via D.build()
        rows: List[D] = []
        for p in primary_items:
            per_lists: Dict[str, List[Any]] = {}
            for src_name in secondary_names:
                key = self.primary_foreign_keys.get(src_name)
                val = getattr(p, key, None) if key else None
                if val is None:
                    per_lists[src_name] = []
                elif isinstance(val, (list, tuple)):
                    per_lists[src_name] = list(val)
                else:
                    per_lists[src_name] = [val]

            if any(len(lst) == 0 for lst in per_lists.values()):
                continue

            if len(secondary_names) == 1:
                sec = secondary_names[0]
                for sec_id in per_lists[sec]:
                    rec = source_records.get(sec, {}).get(sec_id) if sec_id is not None else None
                    row = self.display_model.build(p, {sec: rec})
                    if row is not None:
                        rows.append(row)
            else:
                source_recs: Dict[str, Optional[BaseMongoModel]] = {
                    src_name: (
                        source_records.get(src_name, {}).get(per_lists[src_name][0])
                        if per_lists[src_name][0] is not None else None
                    )
                    for src_name in secondary_names
                }
                row = self.display_model.build(p, source_recs)
                if row is not None:
                    rows.append(row)

        return rows

    # ─────────────────────────────────────────────────────────────────────────
    # get
    # ─────────────────────────────────────────────────────────────────────────

    async def get(self, key_filter_query: Dict[str, Any]) -> Optional[D]:
        decomposed = self._decompose_filter(key_filter_query)
        primary_filter = decomposed.get(self.primary_name, {})
        for fld, val in key_filter_query.items():
            if fld not in self._reverse_field_map:
                primary_filter[fld] = val

        primary = await self._services[self.primary_name].get(primary_filter or key_filter_query)
        if not primary:
            return None

        secondary_names = [n for n in self.sources if n != self.primary_name]
        source_recs: Dict[str, Optional[BaseMongoModel]] = {}

        for src_name in secondary_names:
            key = self.primary_foreign_keys.get(src_name)
            sec_filter = decomposed.get(src_name)
            if sec_filter:
                results = await self._services[src_name].list(filter_query=sec_filter)
                source_recs[src_name] = results[0] if results else None
                continue
            sid = None
            if key:
                raw = getattr(primary, key, None)
                sid = raw[0] if isinstance(raw, (list, tuple)) and raw else raw
            if sid is None:
                source_recs[src_name] = None
            else:
                results = await self._services[src_name].list(filter_query={"_id": sid})
                source_recs[src_name] = results[0] if results else None

        return self.display_model.build(primary, source_recs)