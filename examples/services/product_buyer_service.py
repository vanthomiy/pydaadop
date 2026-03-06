import logging
from typing import List, Optional, Dict, Type, Any

from src.pydaadop.services.interface.read_service_interface import ReadServiceInterface
from src.pydaadop.services.base.base_read_service import BaseReadService
from src.pydaadop.queries.base.base_paging import BasePaging
from src.pydaadop.queries.base.base_sort import BaseSort
from src.pydaadop.queries.base.base_list_filter import BaseListFilter
from src.pydaadop.models.display import DisplayQueryInfo, DisplayItemInfo

from examples.models.buyer import Buyer
from examples.models.demo_product import DemoProduct
from examples.models.payments import Payment
from examples.models.product_buyer_display import ProductBuyerDisplay

log = logging.getLogger(__name__)


class ProductBuyerService(BaseReadService[ProductBuyerDisplay]):
    def __init__(self):
        super().__init__(ProductBuyerDisplay)
        self._payments  = BaseReadService(Payment)
        self._buyers    = BaseReadService(Buyer)
        self._products  = BaseReadService(DemoProduct)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _build(self, payment: Payment, buyer: Buyer, product: DemoProduct) -> ProductBuyerDisplay:
        return ProductBuyerDisplay(
            buyer_id=str(payment.buyer_id),
            buyer_name=buyer.name,
            product_id=str(payment.product_id),
            product_name=product.name,
            amount=payment.amount,
        )

    async def _hydrate(self, payments: List[Payment]) -> List[ProductBuyerDisplay]:
        """Bulk-fetch buyers and products for a list of payments, then assemble rows."""
        if not payments:
            return []

        buyer_ids   = list({p.buyer_id   for p in payments})
        product_ids = list({p.product_id for p in payments})

        buyers   = await self._buyers.list(filter_query={"_id": {"$in": buyer_ids}})
        products = await self._products.list(filter_query={"_id": {"$in": product_ids}})

        buyer_map:   Dict[str, Buyer]       = {str(b.id): b for b in buyers}
        product_map: Dict[str, DemoProduct] = {str(p.id): p for p in products}

        rows: List[ProductBuyerDisplay] = []
        for payment in payments:
            buyer   = buyer_map.get(str(payment.buyer_id))
            product = product_map.get(str(payment.product_id))
            if buyer is None:
                log.warning("Missing buyer %s for payment %s", payment.buyer_id, payment.id)
                continue
            if product is None:
                log.warning("Missing product %s for payment %s", payment.product_id, payment.id)
                continue
            rows.append(self._build(payment, buyer, product))

        return rows

    # ── ReadServiceInterface ──────────────────────────────────────────────────

    async def exists(self, keys_filter_query: dict) -> bool:
        return await self._payments.exists(keys_filter_query)

    async def get(self, keys_filter_query: dict) -> Optional[ProductBuyerDisplay]:
        payment = await self._payments.get(keys_filter_query)
        if payment is None:
            return None
        rows = await self._hydrate([payment])
        return rows[0] if rows else None

    async def list(
        self,
        paging_query: BasePaging = BasePaging(),
        filter_query: Dict = None,
        sort_query: Optional[BaseSort] = None,
        search_query: Dict = None,
        range_query: Dict = None,
        list_filter: BaseListFilter = None,
    ) -> List[ProductBuyerDisplay]:
        payments = await self._payments.list(
            paging_query, filter_query, sort_query, search_query, range_query, list_filter
        )
        return await self._hydrate(payments)

    async def list_keys(
        self,
        keys: List[str],
        filter_query: Dict = None,
        search_query: Dict = None,
        sort_query: Optional[BaseSort] = None,
        range_query: Dict = None,
        list_filter: BaseListFilter = None,
    ) -> List[Dict]:
        return await self._payments.list_keys(
            keys, filter_query, search_query, sort_query, range_query, list_filter
        )

    async def item_info(
        self,
        filter_query: Dict = None,
        search_query: Dict = None,
        range_query: Dict = None,
        list_filter: BaseListFilter = None,
    ) -> DisplayItemInfo:
        return await self._payments.item_info(filter_query, search_query, range_query, list_filter)

    async def query_info(self, model: Type[ProductBuyerDisplay] = ProductBuyerDisplay) -> DisplayQueryInfo:
        return await self._payments.query_info(model)