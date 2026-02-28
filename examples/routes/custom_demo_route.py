from fastapi import APIRouter
from typing import Optional, List, Dict, Any

from ..services.custom_demo_service import CustomDemoService

router = APIRouter()
service = CustomDemoService()


@router.get("/custom-demo/", response_model=List[dict])
async def get_custom_demo(
    product_name: Optional[str] = None, info: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Return combined CustomModel + DemoProduct items filtered by product_name and/or info."""
    return await service.find_combined(product_name=product_name, info=info)
