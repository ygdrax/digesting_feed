"""Helper to load env"""

import json
import os

from dotenv import load_dotenv

load_dotenv()


def load_json_env(var_name, default):
    """Helper to load a JSON-formatted environment variable."""
    try:
        return json.loads(os.getenv(var_name, json.dumps(default)))
    except json.JSONDecodeError:
        print(f"Failed to parse {var_name}, using default.")
        return default


def get_env_var(var_name, default=None):
    """
    Returns the environment variable value.
    If not set, returns the default provided (or None).
    """
    return os.getenv(var_name, default)
