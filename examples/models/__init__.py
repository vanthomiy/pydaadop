"""Expose example models for convenient imports in tests.

This file allows tests to `from examples.models import DemoProduct, Buyer, ProductCategory`.
"""
from .demo_product import DemoProduct
from .buyer import Buyer
from .product_category import ProductCategory
from .product_definition import ProductDefinition

__all__ = ["DemoProduct", "Buyer", "ProductCategory", "ProductDefinition"]
