# utils/create_mongo_uri.py
import os

def get_mongo_uri() -> str | None:
    # Create a dictionary for necessary variables and their values
    env_vars = {
        'MONGODB_USER': os.getenv('MONGODB_USER'),
        'MONGODB_PASS': os.getenv('MONGODB_PASS'),
        'MONGO_BASE_URL': os.getenv('MONGO_BASE_URL'),
        'MONGO_PORT': os.getenv('MONGO_PORT')
    }

    # Check if all required variables are present
    missing_vars = {key: value for key, value in env_vars.items() if value is None}

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars.keys())}")

    # Construct the MONGO_URI
    mongo_uri = f"mongodb://{env_vars['MONGODB_USER']}:{env_vars['MONGODB_PASS']}@" \
                f"{env_vars['MONGO_BASE_URL']}:{env_vars['MONGO_PORT']}"

    return mongo_uri

