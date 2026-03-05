from typing import Optional, List, Dict, Any

from src.pydaadop.routes.base.base_read_route import BaseReadRouter
from examples.models.buyer import Buyer
from examples.services.product_buyer_service import ProductBuyerService
from examples.models.product_buyer_display import ProductBuyerDisplay

class ProductBuyerRoute(BaseReadRouter[ProductBuyerDisplay]):
    """Custom router that extends BaseReadRouter for Buyer and adds a
    `product-buyer` endpoint that returns combined Buyer + DemoProduct data.
    """

    def __init__(self):
        # initialize the underlying many-read-write router with the custom service
        service = ProductBuyerService()
        super().__init__(ProductBuyerDisplay, service)

    def setup_routes(self):
        # keep the base many routes
        super().setup_routes()

