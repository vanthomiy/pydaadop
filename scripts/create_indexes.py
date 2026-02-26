"""Utility script to create MongoDB indexes for all models.

This script is safe to run during deployment and avoids creating indexes at
import time. It imports the application's models and calls BaseMongoDatabase
ensure_indexes synchronously.

Usage: python scripts/create_indexes.py --mongo-uri "mongodb://..."
"""
import argparse
import asyncio
import logging
from typing import List

from pydaadop.database.no_sql.mongodb import BaseMongoDatabase
from pydaadop.models import __all__ as _models  # import-time list of model names

logging.basicConfig(level=logging.INFO)


def main(mongo_uri: str):
    # We create BaseMongoDatabase instances with a real client so ensure_indexes
    # runs against an actual server.
    from motor.motor_asyncio import AsyncIOMotorClient

    client = AsyncIOMotorClient(mongo_uri)

    # Import models dynamically from the package
    import importlib
    from pydaadop.models import __all__ as model_names

    models = []
    for name in model_names:
        module = importlib.import_module(f"pydaadop.models.{name}")
        # The model class is expected to be the only exported attribute in the module
        for attr in dir(module):
            if attr.startswith("_"):
                continue
            maybe = getattr(module, attr)
            try:
                if isinstance(maybe, type):
                    models.append(maybe)
            except Exception:
                continue

    # Create indexes for each model
    for model in models:
        db = BaseMongoDatabase(model, client=client)
        # _ensure_connection will create the collection and schedule/create indexes
        db._ensure_connection()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mongo-uri", default="mongodb://localhost:27017")
    args = parser.parse_args()
    main(args.mongo_uri)
