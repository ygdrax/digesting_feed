"""Module for storing and managing articles in JSON format."""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict
from .helper import helper

RETENTION_DAYS = 7


def save_articles_to_json(articles: List[Dict], relative_path: str = "data/articles.json"):
    """
    Save articles. Append new articles unless oldest stored article is older than retention period.

    Args:
        articles (List[Dict]): List of new articles to save.
        relative_path (str): Relative path for JSON storage.
    """
    full_path = helper.get_full_path(relative_path, must_exist=False)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    existing_articles = []
    if os.path.exists(full_path):
        existing_articles = load_articles_from_json(relative_path)

    # Combine and deduplicate articles
    all_articles = remove_duplicates_by_link(existing_articles + articles)

    # Filter articles older than retention days if needed
    dates = []
    for a in all_articles:
        if "date" in a:
            try:
                dates.append(datetime.strptime(a["date"], "%Y-%m-%d"))
            except ValueError:
                # Skip articles with invalid date format
                continue
    if dates:
        oldest = min(dates)
        newest = max(dates)
        age_days = (newest - oldest).days
        if age_days > RETENTION_DAYS:
            cutoff = newest - timedelta(days=RETENTION_DAYS)
            all_articles = [
                a
                for a in all_articles
                if "date" in a and datetime.strptime(a["date"], "%Y-%m-%d") >= cutoff
            ]

    # Write updated articles back to JSON
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)


def load_articles_from_json(relative_path: str = "data/articles.json") -> List[Dict]:
    """
    Load a list of article dictionaries from a JSON file.

    Args:
        relative_path (str): Relative path of JSON file to load.

    Returns:
        List[Dict]: List of article dictionaries.
    """
    full_path = helper.get_full_path(relative_path, must_exist=True)
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


def remove_duplicates_by_link(articles: List[Dict]) -> List[Dict]:
    """
    Remove duplicate articles based on their 'link' field.

    Args:
        articles (List[Dict]): List of articles to deduplicate.

    Returns:
        List[Dict]: Deduplicated list of articles.
    """
    seen = set()
    unique = []
    for article in articles:
        link = article.get("link")
        if link and link not in seen:
            seen.add(link)
            unique.append(article)
    return unique
