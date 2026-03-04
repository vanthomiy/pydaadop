from typing import Optional, List, Dict, Any

from pydaadop.routes.many.many_read_write_route import ManyReadWriteRouter
from examples.models.buyer import Buyer
from ..services.product_buyer_service import ProductBuyerService


class ProductBuyerRoute(ManyReadWriteRouter[Buyer]):
    """Custom router that extends ManyReadWriteRouter for Buyer and adds a
    `product-buyer` endpoint that returns combined Buyer + DemoProduct data.
    """

    def __init__(self):
        # initialize the underlying many-read-write router with the custom service
        service = ProductBuyerService()
        super().__init__(Buyer, service)

    def setup_routes(self):
        # keep the base many routes
        super().setup_routes()

        # add the custom combined view
        @self.router.get("/product-buyer/", response_model=List[dict])
        async def get_product_buyer(product_name: Optional[str] = None, info: Optional[str] = None) -> List[Dict[str, Any]]:
            return await self.service.find_combined(product_name=product_name, info=info)


# export the router instance for inclusion by the demo app
router = ProductBuyerRoute().router
