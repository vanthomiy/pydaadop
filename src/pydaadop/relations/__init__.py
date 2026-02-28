"""Relations utilities for declarative Pydantic Field metadata and bulk loading.

This module implements:
- Relation dataclass describing relation metadata
- helpers to read relation metadata from Pydantic models (Field extras)
- a bulk async loader `load_relations` which performs one query per relation
  and maps results back to provided model instances.

Design: Fields use `Field(..., relation={...})` extras. See README/docs for usage.
"""

from .core import (
    Relation,
    get_relations_for_model,
    load_relations,
    normalize_id,
    register_repo,
    get_repo,
    clear_repo_registry,
)

__all__ = [
    "Relation",
    "get_relations_for_model",
    "load_relations",
    "normalize_id",
    "register_repo",
    "get_repo",
    "clear_repo_registry",
]
