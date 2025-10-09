"""Helper  module accros module"""

from datetime import datetime
from pathlib import Path


def get_full_path(relative_path: str, must_exist: bool = False) -> str:
    """
    Resolves the full absolute path from a relative one based on current script location.

    Args:
        relative_path (str): Relative path to file.
        must_exist (bool): Whether to raise error if file does not exist.

    Returns:
        str: Full absolute path.
    """
    base_dir = Path(__file__).resolve().parent
    full_path = base_dir / ".." / relative_path

    if must_exist and not full_path.exists():
        raise FileNotFoundError(f"File not found at: {full_path}")

    return str(full_path.resolve())


def get_current_timestamp() -> str:
    """
    Get current timestamp as formatted string.
    
    Returns:
        str: Current timestamp in YYYY-MM-DD HH:MM:SS format
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
