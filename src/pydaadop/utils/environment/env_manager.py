"""
This module provides utilities for managing environment variables related to MongoDB connections.

Functions:
    get_mongo_uri: Constructs a MongoDB URI from environment variables.
"""

import os

def get_mongo_uri() -> str | None:
    """
    Constructs a MongoDB URI from environment variables.

    This function reads the following environment variables:
    - MONGO_CONNECTION_STRING: The MongoDB connection string.
    - MONGODB_USER: The MongoDB username.
    - MONGODB_PASS: The MongoDB password.
    - MONGO_BASE_URL: The base URL of the MongoDB server.
    - MONGO_PORT: The port number of the MongoDB server.

    It then constructs and returns a MongoDB URI in the format:
    `mongodb://<MONGODB_USER>:<MONGODB_PASS>@<MONGO_BASE_URL>:<MONGO_PORT>`

    Raises:
        ValueError: If any of the required environment variables are missing.

    Returns:
        str: The constructed MongoDB URI.

    Example:
        >>> os.environ['MONGODB_USER'] = 'user'
        >>> os.environ['MONGODB_PASS'] = 'pass'
        >>> os.environ['MONGO_BASE_URL'] = 'localhost'
        >>> os.environ['MONGO_PORT'] = '27017'
        >>> get_mongo_uri()
        'mongodb://user:pass@localhost:27017'
    """
    # Create a dictionary for necessary variables and their values
    env_vars = {
        'MONGO_CONNECTION_STRING': os.getenv('MONGO_CONNECTION_STRING'),
        'MONGODB_USER': os.getenv('MONGODB_USER'),
        'MONGODB_PASS': os.getenv('MONGODB_PASS'),
        'MONGO_BASE_URL': os.getenv('MONGO_BASE_URL'),
        'MONGO_PORT': os.getenv('MONGO_PORT')
    }

    # check if there is a connection string, then don't build the mongo uri
    if env_vars['MONGO_CONNECTION_STRING'] is not None:
        return env_vars['MONGO_CONNECTION_STRING']
    
    # Check if all required variables are present
    missing_vars = {key: value for key, value in env_vars.items() if value is None}

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars.keys())}")

    # Construct the MONGO_URI
    mongo_uri = f"mongodb://{env_vars['MONGODB_USER']}:{env_vars['MONGODB_PASS']}@" \
                f"{env_vars['MONGO_BASE_URL']}:{env_vars['MONGO_PORT']}"

    return mongo_uri

