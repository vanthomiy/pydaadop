from typing import List, Optional, Dict, Any

from pydaadop.repositories.base.base_read_repository import BaseReadRepository
from pydaadop.relations.core import load_relations, get_repo

from examples.models.custom_model import CustomModel
from examples.models.demo_product import DemoProduct


class CustomDemoService:
    """Small example service that demonstrates combining CustomModel and DemoProduct data."""

    def __init__(self):
        self.custom_repo = BaseReadRepository(CustomModel)
        # Prefer a registered repo (useful for demos without a running MongoDB).
        # If no registered repo exists, fall back to the BaseReadRepository which
        # connects to Mongo when available.
        self.product_repo = get_repo("demoproduct") or BaseReadRepository(DemoProduct)

    async def find_combined(
        self, product_name: Optional[str] = None, info: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # If product_name provided, resolve matching product ids first
        filter_query: Dict = {}
        if product_name:
            products = await self.product_repo.list(filter_query={"name": product_name})
            pids = [p.id for p in products]
            if pids:
                filter_query["product_id"] = {"$in": pids}

        if info:
            filter_query["info"] = info

        items = await self.custom_repo.list(filter_query=filter_query)

        # Bulk load the product relation for the items
        await load_relations(
            items, include=["product"], repos={"demoproduct": self.product_repo}
        )

        # Serialize for the API consumer
        return [it.model_dump() for it in items]
