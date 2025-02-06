from abc import ABC
from typing import TypeVar, Type, List
from pydantic import BaseModel
from pymongo.results import InsertManyResult, BulkWriteResult, DeleteResult
from typing_extensions import override

from ..base.base_read_write_service import BaseReadWriteService
from ..interface.many_read_write_service_interface import ManyReadWriteServiceInterface
from ...models.base import BaseMongoModel
from ...repositories.many.many_read_write_repository import ManyReadWriteRepository

S = TypeVar('S', bound=BaseMongoModel)
R = TypeVar('R', bound=ManyReadWriteRepository[BaseMongoModel])

class ManyReadWriteService(ManyReadWriteServiceInterface[S], BaseReadWriteService[S], ABC):
    def __init__(self, model: Type[S], repository: R = None):
        self.repository = repository if repository else ManyReadWriteRepository(model)
        super().__init__(model, self.repository)

    @override
    async def create_many(self, items: [S]) -> InsertManyResult:
        return await self.repository.create_many(items)

    @override
    async def update_many(self, items: [S]) -> BulkWriteResult:
        return await self.repository.update_many(items)

    @override
    async def update_field_many(self, key_filter_queries: List[dict], data: dict) -> BulkWriteResult:
        return await self.repository.update_field_many(key_filter_queries, data)

    @override
    async def delete_many(self, key_filter_queries: List[dict]) -> DeleteResult:
        return await self.repository.delete_many(key_filter_queries)
