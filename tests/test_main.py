"""Tests for the main module."""

from datetime import datetime
from unittest.mock import patch

import pytest

from digesting_feed.main import score_article, main

# -------------------------
# Test: score_article
# -------------------------


@pytest.mark.parametrize(
    "title,source,expected_score",
    [
        ("DevOps and Cloud", "Netflix", 2 + 3),
        ("Observability with Kubernetes", "Hacker News", 2 + 2),
        ("Networking in Linux", "Unknown Source", 2 + 0),
        ("Random Post", "Reddit", 0 + 1),
        ("", "Reddit", 0 + 1),
    ],
)
def test_score_article(title, source, expected_score):
    """Test scoring logic for articles."""
    article = {"title": title, "source": source}
    assert score_article(article) == expected_score


# -------------------------
# Test: main function
# -------------------------


@patch("digesting_feed.main.fetch_hn_articles")
@patch("digesting_feed.main.fetch_reddit_articles")
@patch("digesting_feed.main.fetch_tech_blog_articles")
@patch("digesting_feed.main.manage_article.save_articles_to_json")
@patch("digesting_feed.main.generate_html")
@patch("digesting_feed.main.manage_article.load_articles_from_json", return_value=[])
def test_main_execution(
    _mock_load_json,
    mock_generate_html,
    mock_save_json,
    mock_fetch_tech,
    mock_fetch_reddit,
    mock_fetch_hn,
):
    """Test main() end-to-end with mocked fetchers and storage."""
    mock_articles = [
        {
            "title": "Cloud Infra at Netflix",
            "link": "https://a.com",
            "source": "Netflix",
        },
        {"title": "Monitoring Kubernetes", "link": "https://b.com", "source": "Reddit"},
        {"title": "AI in DevOps", "link": "https://c.com", "source": "Google"},
    ]

    # Set up each fetcher to return one item
    mock_fetch_hn.return_value = [mock_articles[0]]
    mock_fetch_reddit.return_value = [mock_articles[1]]
    mock_fetch_tech.return_value = [mock_articles[2]]

    main()

    # Assert all expected calls happened
    assert mock_save_json.called
    assert mock_generate_html.called

    saved_articles = mock_save_json.call_args[0][0]
    assert len(saved_articles) == 3

    for article in saved_articles:
        assert "score" in article
        assert "date" in article
        # Ensure today's date is attached
        assert article["date"] == datetime.now().strftime("%Y-%m-%d")
