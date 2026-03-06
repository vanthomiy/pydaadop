from typing import ClassVar, Dict, List, Type, Any, Optional, TYPE_CHECKING
from ...models.base.base_mongo_model import BaseMongoModel


def _normalize_name(cls: type) -> str:
    name = cls.__name__.lower()
    if name.endswith("model"):
        name = name[:-5]
    return name


class DisplayBaseModel(BaseMongoModel):
    """
    Base class for all display models used with GenericDisplayService.

    Subclasses declare the full mapping contract as class variables,
    and get automatic row construction via build().

    Required class variables:
        sources          – source models in order; FIRST is primary
        source_field_map – {display_field: (source_name, source_field)}
        indexes          – display fields to index on

    Row construction:
        DisplayBaseModel.build(sources_dict) is called by GenericDisplayService
        to assemble each row. The default implementation reads source_field_map
        automatically. Override build() on the display model for custom logic.

    Example:
        class ProductBuyerDisplay(DisplayBaseModel):
            product_id:   str
            buyer_id:     str
            product_name: str
            buyer_name:   str
            amount:       Optional[int] = None

            sources          = [Payment, Buyer, DemoProduct]
            source_field_map = {
                "buyer_id":     ("payment",     "buyer_id"),
                "product_id":   ("payment",     "product_id"),
                "amount":       ("payment",     "amount"),
                "buyer_name":   ("buyer",       "name"),
                "product_name": ("demoproduct", "name"),
            }
            indexes = ["product_id", "buyer_id"]

            # Optional: override build() for custom logic
            @classmethod
            def build(cls, primary: Payment, sources: dict) -> "ProductBuyerDisplay | None":
                buyer   = sources.get("buyer")
                product = sources.get("demoproduct")
                if not buyer or not product:
                    return None
                return cls(
                    buyer_id=str(primary.buyer_id),
                    buyer_name=buyer.name,
                    ...
                )
    """

    sources: ClassVar[List[Type[BaseMongoModel]]]
    source_field_map: ClassVar[Dict[str, tuple[str, str]]]
    indexes: ClassVar[List[str]]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        # Skip intermediary classes that don't define the contract yet
        if not all(hasattr(cls, attr) for attr in ("sources", "source_field_map", "indexes")):
            return

        if not cls.sources:
            raise TypeError(f"{cls.__name__}.sources must be a non-empty list.")

        declared = {_normalize_name(m) for m in cls.sources}
        for display_field, (src_name, src_field) in cls.source_field_map.items():
            if src_name not in declared:
                raise TypeError(
                    f"{cls.__name__}.source_field_map['{display_field}'] references "
                    f"source '{src_name}' which is not in sources {declared}."
                )

        all_annotations: Dict[str, Any] = {}
        for klass in reversed(cls.__mro__):
            all_annotations.update(getattr(klass, "__annotations__", {}))
        for idx_field in cls.indexes:
            if idx_field not in all_annotations:
                raise TypeError(
                    f"{cls.__name__}.indexes references '{idx_field}' "
                    f"which is not an annotated field."
                )

    @classmethod
    def build(
        cls,
        primary: BaseMongoModel,
        sources: Dict[str, Optional[BaseMongoModel]],
    ) -> "DisplayBaseModel | None":
        """
        Assemble a display row from source model instances.

        Default: reads source_field_map and pulls attributes automatically.
        Override in subclasses for validation, transformation, or custom logic.

        Return None to discard the row (e.g. missing required secondary).
        """
        primary_name = _normalize_name(type(primary))
        row: Dict[str, Any] = {}
        for display_field, (src_name, src_field) in cls.source_field_map.items():
            if src_name == primary_name:
                row[display_field] = getattr(primary, src_field, None)
            else:
                rec = sources.get(src_name)
                row[display_field] = getattr(rec, src_field, None) if rec is not None else None
        return cls(**row)

    @classmethod
    def create_index(cls) -> List[str]:
        return cls.indexes