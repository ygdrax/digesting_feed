"""Module for storing and managing articles in JSON format."""

import json
from pathlib import Path
from typing import List, Dict

from .helper import helper


def save_articles_to_json(articles: List[Dict], relative_path: str = "data/articles.json") -> None:
    """Save articles to JSON file."""
    full_path = helper.get_full_path(relative_path, must_exist=False)
    Path(full_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def load_articles_from_json(relative_path: str = "data/articles.json") -> List[Dict]:
    """Load articles from JSON file."""
    full_path = helper.get_full_path(relative_path, must_exist=True)
    with open(full_path, encoding="utf-8") as f:
        return json.load(f)
