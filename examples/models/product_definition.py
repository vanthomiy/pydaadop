from enum import Enum


class ProductDefinition(str, Enum):
    A = 'allow'
    B = 'below'
    C = 'celow'
