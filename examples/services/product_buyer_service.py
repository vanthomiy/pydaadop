from typing import Dict, Optional
from typing_extensions import override
from src.pydaadop.services.display.generic_display_service import GenericDisplayService
from examples.models.buyer import Buyer
from examples.models.demo_product import DemoProduct
from examples.models.product_buyer_display import ProductBuyerDisplay


class ProductBuyerService(GenericDisplayService[ProductBuyerDisplay, Buyer, DemoProduct]):
    def __init__(self):
        super().__init__(
            ProductBuyerDisplay,
            Buyer,        # ← primary (first = primary rule)
            DemoProduct,  # ← secondary
            # "buyer.products" holds the list of DemoProduct ids
            primary_foreign_keys={"demoproduct": "products"},
        )

        for svc in self._services.values():
            try:
                svc.create_index()
            except Exception:
                pass
    
    @override
    def mapping(self, buyer: Buyer, sources: Dict[str, Optional[DemoProduct]]) -> ProductBuyerDisplay:
        product: Optional[DemoProduct] = sources.get("demoproduct")
        return ProductBuyerDisplay(
            buyer_id=buyer._id,
            buyer_name=buyer.name,
            product_id=product._id if product else None,
            product_name=product.name if product else None,
            amount=1,
        )