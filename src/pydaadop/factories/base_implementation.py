# core/factories/base_implementation.py

from abc import ABC, abstractmethod
from typing import Optional, Dict


class BaseImplementation(ABC):
    @abstractmethod
    def is_factory(self, value) -> bool:
        pass


