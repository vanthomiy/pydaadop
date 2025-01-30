# core/factories/base_factory.py
from abc import ABC
from typing import TypeVar

from ..factories.base_implementation import BaseImplementation

S = TypeVar('S', bound=BaseImplementation)


class BaseFactory(ABC):

    def __init__(self, factories: list[S]):
        self.factories = factories

    def get_implementation(self, value) -> BaseImplementation or None:
        for factory in self.factories:
            if factory.is_factory(value):
                return factory
        return None
