from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type
import asyncio
import string

from bson import ObjectId

from pydantic import BaseModel

from ..models.base.base_mongo_model import BaseMongoModel
from .dataloader import RequestDataLoaderRegistry


@dataclass
class Relation:
    name: str
    by: str  # attribute name that stores the id (e.g., 'athlete_id')
    model: Optional[Type[BaseMongoModel]] = None
    repo_key: Optional[str] = None
    many: bool = False
    include_by_default: Optional[bool] = False
    projection: Optional[Dict[str, Any]] = None


def normalize_id(value: Any) -> Any:
    """Normalize an id value to ObjectId when it looks like one, otherwise keep as-is.

    Returns the original value or an ObjectId instance.
    """
    if isinstance(value, ObjectId):
        return value
    if (
        isinstance(value, str)
        and len(value) == 24
        and all(c in string.hexdigits for c in value)
    ):
        try:
            return ObjectId(value)
        except Exception:
            return value
    return value


# Simple repository registry to allow resolving repos by key when loading relations
_REPO_REGISTRY: Dict[str, Any] = {}


def register_repo(key: str, repo: Any) -> None:
    _REPO_REGISTRY[key] = repo


def get_repo(key: str) -> Optional[Any]:
    return _REPO_REGISTRY.get(key)


def clear_repo_registry() -> None:
    _REPO_REGISTRY.clear()


# Per-request dataloader registry (caller may replace per request)
DEFAULT_DATALOADER_REGISTRY = RequestDataLoaderRegistry()


def get_relations_for_model(model: Type[BaseModel]) -> Dict[str, Relation]:
    """Read relation Field metadata from a Pydantic model.

    Expects fields to have `field_info.extra['relation']` with keys matching Relation.
    """
    relations: Dict[str, Relation] = {}
    fields = getattr(model, "__fields__", {})
    for name, field in fields.items():
        extra = getattr(field, "field_info", None)
        if not extra:
            continue
        meta = getattr(extra, "extra", {})
        rel = meta.get("relation")
        if not rel:
            continue
        # Build Relation dataclass from provided metadata
        r = Relation(
            name=name,
            by=rel.get("by") or f"{name}_id",
            model=rel.get("model"),
            repo_key=rel.get("repo"),
            many=bool(rel.get("many", False)),
            include_by_default=rel.get("include_by_default", False),
            projection=rel.get("projection"),
        )
        relations[name] = r
    return relations


async def load_relations(
    items: Sequence[BaseMongoModel],
    include: Optional[Sequence[str]] = None,
    exclude: Optional[Sequence[str]] = None,
    repos: Optional[Dict[str, Any]] = None,
    chunk_size: int = 1000,
):
    """Bulk load relations for a list of model instances.

    - items: list of BaseMongoModel instances (or objects with attributes)
    - include: list of relation names to include (None = include those with include_by_default True)
    - exclude: list of relation names to exclude
    - repos: mapping of repo_key -> repository instance (must implement `get_many_by_ids`)
    """
    if not items:
        return

    model_cls = type(items[0])
    relations = get_relations_for_model(model_cls)
    if not relations:
        return

    include_set = set(include or [])
    exclude_set = set(exclude or [])

    # Determine which relations to process
    to_process: List[Relation] = []
    for name, rel in relations.items():
        if name in exclude_set:
            continue
        if include is None:
            if rel.include_by_default:
                to_process.append(rel)
        else:
            if name in include_set:
                to_process.append(rel)

    # For each relation, collect ids and query repos
    async def _process_relation(rel: Relation):
        id_values = set()
        for item in items:
            raw = getattr(item, rel.by, None)
            if raw is None:
                continue
            if rel.many and isinstance(raw, (list, tuple)):
                for r in raw:
                    nid = normalize_id(r)
                    if nid is not None:
                        id_values.add(str(nid))
            else:
                nid = normalize_id(raw)
                if nid is not None:
                    id_values.add(str(nid))

        if not id_values:
            return

        # Resolve repository to use
        repo = None
        if repos and rel.repo_key:
            repo = repos.get(rel.repo_key)

        # Default repo: try to use model name lower
        if repo is None and rel.model is not None:
            # repo key default
            repo_key = rel.model.__name__.lower()
            if repos:
                repo = repos.get(repo_key)
            if repo is None:
                repo = get_repo(repo_key)

        # If still no repo, attempt to construct a BaseReadRepository for the model
        if repo is None and rel.model is not None:
            try:
                from ..repositories.base.base_read_repository import BaseReadRepository

                repo = BaseReadRepository(rel.model)
            except Exception:
                repo = None

        if repo is None:
            raise RuntimeError(f"No repository found for relation {rel.name}")

        # chunk ids
        ids_list = list(id_values)
        fetched_items = []
        for i in range(0, len(ids_list), chunk_size):
            chunk = ids_list[i : i + chunk_size]
            # Expect repo to implement get_many_by_ids(ids: List[str|ObjectId]) -> List[model]
            if rel.projection is not None:
                got = await repo.get_many_by_ids(
                    [normalize_id(x) for x in chunk], projection=rel.projection
                )
            else:
                got = await repo.get_many_by_ids([normalize_id(x) for x in chunk])
            fetched_items.extend(got)

        # Build map by stringified id
        byid = {
            str(getattr(x, "id", getattr(x, "_id", None))): x for x in fetched_items
        }

        # Attach to each item
        for item in items:
            raw = getattr(item, rel.by, None)
            if raw is None:
                setattr(item, rel.name, None if not rel.many else [])
                continue
            if rel.many and isinstance(raw, (list, tuple)):
                out = [
                    byid.get(str(normalize_id(r)))
                    for r in raw
                    if byid.get(str(normalize_id(r)))
                ]
                setattr(item, rel.name, out)
            else:
                setattr(item, rel.name, byid.get(str(normalize_id(raw))))

    # Run relation tasks in parallel
    await asyncio.gather(*[_process_relation(r) for r in to_process])
