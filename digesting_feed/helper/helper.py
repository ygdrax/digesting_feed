"""Helper  module accros module"""

import os


def get_full_path(relative_path: str, must_exist: bool = False) -> str:
    """
    Resolves the full absolute path from a relative one based on current script location.

    Args:
        relative_path (str): Relative path to file.
        must_exist (bool): Whether to raise error if file does not exist.

    Returns:
        str: Full absolute path.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, "..", relative_path)

    if must_exist and not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found at: {full_path}")

    return os.path.abspath(full_path)
