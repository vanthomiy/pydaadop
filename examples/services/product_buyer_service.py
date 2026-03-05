from examples.models.product_buyer_display import ProductBuyerDisplay
from examples.models.buyer import Buyer
from examples.models.demo_product import DemoProduct
from src.pydaadop.services.display.generic_display_service import GenericDisplayService


class ProductBuyerService(GenericDisplayService):
    def __init__(self):
        sources = [Buyer, DemoProduct]
        # Only provide a constant mapping for amount; other fields are inferred
        field_map = {"amount": {"constant": 1}}
        super().__init__(ProductBuyerDisplay, primary=Buyer, sources=sources, field_map=field_map)

        # ensure indexes exist for underlying services (best-effort)
        for svc in self._services.values():
            try:
                svc.create_index()
            except Exception:
                pass

    

