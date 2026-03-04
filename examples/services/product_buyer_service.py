from typing import List, Optional, Dict, Any, Type

from pydaadop.repositories.base.base_read_repository import BaseReadRepository
from pydaadop.relations.core import load_relations
from pydaadop.services.many.many_read_write_service import ManyReadWriteService

from examples.models.buyer import Buyer
from examples.models.demo_product import DemoProduct


class ProductBuyerService(ManyReadWriteService[Buyer]):
    """Service that extends ManyReadWriteService for Buyer and combines DemoProduct relations.

    Provides the usual many-create/update/delete operations via the base class
    and adds a `find_combined` helper that resolves product relations.
    """

    def __init__(self):
        # initialize base many service for Buyer
        super().__init__(Buyer)
        # separate read repository for products used to resolve relations
        self.product_repo = BaseReadRepository(DemoProduct)

    async def find_combined(
        self, product_name: Optional[str] = None, info: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # Build filter for buyers based on product name or info
        filter_query: Dict = {}
        if product_name:
            products = await self.product_repo.list(filter_query={"name": product_name})
            pids = [p.id for p in products]
            if pids:
                filter_query["product_id"] = {"$in": pids}

        if info:
            filter_query["info"] = info

        # Use the service's list method to get buyer items
        items = await self.list(filter_query=filter_query)

        # Bulk load the product relation for the items
        await load_relations(items, include=["product"], repos={"demoproduct": self.product_repo})

        # Serialize for the API consumer
        return [it.model_dump() for it in items]
