# pydaadop: two small fixes (truthiness + issubclass guard)

## Summary
Two reproducible runtime bugs when using `pydaadop` with current pymongo / typing constructs:
- Collections are tested for truthiness (`if collection:`) which raises NotImplementedError for PyMongo/Motor `Collection` objects.
- `BaseQuery._get_type` calls `issubclass(origin, Enum)` where `origin` can be a typing-origin (not a class), causing `TypeError: issubclass() arg 1 must be a class`.

---

## Tasks (copyable)

- [ ] Fix collection truthiness in `pydaadop/repositories/base/base_repository.py`
- [ ] Guard `issubclass` checks and improve typing-origin handling in base_query.py
- [ ] Add unit tests reproducing both failures
- [ ] Bump package version and add changelog entry
- [ ] Open PR with patches, tests, and CI passing
- [ ] Pin patched release in downstream `requirements.txt`/Dockerfile

---

## 1) Fix: collection truthiness
File: `pydaadop/repositories/base/base_repository.py`

Problem (original line):
```py
self.collection = collection if collection else BaseMongoDatabase(model).collection
```

Exact change (replace truth test with explicit None check):
```py
# Before:
# self.collection = collection if collection else BaseMongoDatabase(model).collection

# After:
self.collection = collection if collection is not None else BaseMongoDatabase(model).collection
```

Reproduction
```py
from pymongo import MongoClient
from pydaadop.repositories.base.base_repository import BaseRepository
# create a real pymongo Collection
client = MongoClient("mongodb://localhost:27017")
collection = client.test.mycoll
# should NOT raise NotImplementedError
repo = BaseRepository(MyModel, collection)
```

Unit test (pytest)
```py
def test_base_repository_accepts_collection(pymongo_client, MyModel):
    coll = pymongo_client.test.mycoll
    repo = BaseRepository(MyModel, collection=coll)
    assert repo.collection is coll
```

---

## 2) Fix: guard issubclass checks in `_get_type`
File: `pydaadop/queries/base/base_query.py`

Problem (offending snippet):
```py
# origin may not be a class (e.g., typing constructs) so guard issubclass
if isinstance(origin, type) and issubclass(origin, Enum):
    return str, True
```
(If the file currently has unguarded `issubclass(origin, Enum)` you must guard it.)

Recommended safe replacement — full guarded `_get_type` implementation (robust for `Literal`, `Optional`, nested args and Enum handling):

```py
from enum import Enum
from typing import get_origin, get_args, Literal

@classmethod
def _get_type(cls, annotation: Any) -> Tuple[type | None, bool]:
    if not annotation:
        return None, False

    origin = get_origin(annotation) or annotation
    args = get_args(annotation)

    if origin in cls.supported_types:
        return origin, False
    if args and (args[0] in cls.supported_types):
        return args[0], False

    if origin == Literal:
        literal_type = type(args[0]) if args else None
        if literal_type in cls.supported_types:
            return literal_type, True
        return None, False

    # Guard issubclass check: ensure origin is a class first
    if isinstance(origin, type) and issubclass(origin, Enum):
        return str, True

    # Recursively handle nested typing args
    if args and origin is not None:
        return cls._get_type(args[0])

    return None, False
```

Reproduction
```py
from typing import Literal, Optional
from pydaadop.queries.base.base_query import BaseQuery

# Should NOT raise TypeError
BaseQuery._get_type(Literal['a'])       # -> (str, True) or similar
BaseQuery._get_type(Optional[MyEnum])   # -> (str, True) when MyEnum is Enum subclass
```

Unit test (pytest)
```py
def test_get_type_literal():
    t, selectable = BaseQuery._get_type(Literal["x", "y"])
    assert t is str
    assert selectable is True

def test_get_type_enum_optional():
    class E(Enum):
        A = "a"
    t, selectable = BaseQuery._get_type(Optional[E])
    assert t is str
    assert selectable is True
```

---

## 3) Unit tests
- Add tests under `tests/`:
  - `tests/test_repository.py` — the `BaseRepository` collection-acceptance test
  - `tests/test_base_query.py` — tests above for `Literal` and Enum cases
- Use CI to run tests with a real or mocked `pymongo` `Collection`. For real integration, run a local `mongod` or use a test container.

Example pytest commands:
```bash
pytest -q
# or run a specific test
pytest tests/test_base_query.py::test_get_type_literal -q
```

---

## 4) PR checklist / description (copy-paste)

Title: Fix collection truthiness and guard typing-origin checks in BaseQuery

Description:
- Replace truthiness check on `collection` with `collection is not None` to avoid NotImplementedError from PyMongo/Motor Collections.
- Guard `issubclass` usage in `BaseQuery._get_type` so typing-origin values (e.g. `Literal`, `Union`) don't raise `TypeError`.
- Add unit tests reproducing both failures.
- Add CHANGELOG entry and bump version.

Files changed:
- `pydaadop/repositories/base/base_repository.py` — one-line fix
- `pydaadop/queries/base/base_query.py` — guarded `_get_type` implementation
- `tests/test_repository.py` — new
- `tests/test_base_query.py` — new
- `CHANGELOG.md`, `pyproject.toml`/`setup.cfg` version bump

Testing:
- `pytest` passes locally and in CI.

Notes:
- These are defensive changes; they don't change public behavior for valid inputs but prevent crashes on typing constructs and on proper `Collection` objects.

---

## 5) Release / downstream
- After merge, bump to `x.y.z` and upload a patch release.
- Downstream pin in `requirements.txt`:
  - `pydaadop==x.y.z`
  - or temporarily: `git+https://github.com/<you>/pydaadop@branch-or-commit#egg=pydaadop` until upstream release.

Docker build note (if you prefer image-only fix before release):
- In `Dockerfile` you can pip-install from the fork:
```dockerfile
RUN pip install --no-cache-dir git+https://github.com/<you>/pydaadop@fix-collection-issubclass
```

---

## Suggested commit messages
- `fix: explicit None check for collection in BaseRepository`
- `fix: guard issubclass checks in BaseQuery._get_type and handle Literal/typing origins`
- `test: add tests for collection acceptance and BaseQuery._get_type`
