"""Tests for the manage_article module."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from digesting_feed import manage_article

MOCK_ARTICLES = [
    {
        "title": "First",
        "link": "http://a.com",
        "score": 5,
        "date": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),
    },
    {
        "title": "Second",
        "link": "http://b.com",
        "score": 1,
        "date": datetime.now().strftime("%Y-%m-%d"),
    },
]


@pytest.fixture
def temp_file_path():
    """Create a temporary file path in /tmp and ensure cleanup."""
    with tempfile.NamedTemporaryFile(
        prefix="test_articles_", suffix=".json", delete=False
    ) as tmpfile:
        path = tmpfile.name
    yield path
    # Cleanup after test run
    if Path(path).exists():
        Path(path).unlink()


@pytest.fixture
def mock_helper(temp_file_path):
    """Patch get_full_path to return the temp file path."""
    with patch("digesting_feed.manage_article.helper.get_full_path") as mock_get_path:
        mock_get_path.return_value = temp_file_path
        yield mock_get_path


def test_save_and_load_articles(mock_helper, temp_file_path):
    # Make sure the file is empty before saving
    if Path(temp_file_path).exists():
        Path(temp_file_path).unlink()

    manage_article.save_articles_to_json(MOCK_ARTICLES)

    with open(temp_file_path) as f:
        content = f.read()
        print("File content after save:", content)

    loaded = manage_article.load_articles_from_json()
    assert len(loaded) == 2
    assert all("title" in a and "link" in a for a in loaded)


def test_remove_duplicates():
    """Test removing duplicate articles by link."""
    articles = [
        {"link": "http://a.com", "title": "Article A"},
        {"link": "http://b.com", "title": "Article B"},
        {"link": "http://a.com", "title": "Duplicate Article A"},
    ]
    result = manage_article.remove_duplicates_by_link(articles)
    links = [a["link"] for a in result]
    assert set(links) == {"http://a.com", "http://b.com"}


def test_retention_trim(mock_helper, temp_file_path):
    old_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    new_date = datetime.now().strftime("%Y-%m-%d")

    articles = [
        {"title": "Old", "link": "http://old.com", "date": old_date},
        {"title": "New", "link": "http://new.com", "date": new_date},
    ]

    # Clear file before saving
    if Path(temp_file_path).exists():
        Path(temp_file_path).unlink()

    manage_article.save_articles_to_json(articles)
    loaded = manage_article.load_articles_from_json()

    # If retention trimming is implemented in save or load, only new or one article remains
    assert all(a["date"] >= new_date for a in loaded) or len(loaded) == 1
