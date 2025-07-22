"""Tests for the fetcher module."""

from unittest.mock import patch, MagicMock
from digesting_feed.fetcher import (
    clean_html,
    fetch_hn_articles,
    fetch_reddit_articles,
    fetch_tech_blog_articles,
)


# -------------------------------------
# clean_html
# -------------------------------------
def test_clean_html_removes_tags_and_truncates():
    """Test that clean_html removes HTML tags and truncates text."""
    raw_html = "<p>Hello <b>World</b>! <script>alert('XSS')</script></p>"
    clean = clean_html(raw_html)
    assert "Hello World!" in clean
    assert "<" not in clean
    assert len(clean) <= 300


# -------------------------------------
# fetch_hn_articles
# -------------------------------------
@patch("digesting_feed.fetcher.feedparser.parse")
def test_fetch_hn_articles(mock_parse):
    """Test fetching articles from Hacker News."""
    mock_entry = MagicMock()
    mock_entry.title = "Hacker News Test"
    mock_entry.link = "https://hn.com/1"
    mock_entry.get = MagicMock(return_value="<p>Hacker news</p>")  # for entry.get("summary", "")
    mock_parse.return_value.entries = [mock_entry]

    articles = fetch_hn_articles()
    assert len(articles) == 1
    assert articles[0]["source"] == "Hacker News"
    assert "Hacker News Test" in articles[0]["title"]
    assert "https://hn.com/1" in articles[0]["link"]
    assert "summary" in articles[0]
    assert articles[0]["score"] == 0


# -------------------------------------
# fetch_reddit_articles
# -------------------------------------
@patch("digesting_feed.fetcher.requests.get")
@patch("digesting_feed.fetcher.feedparser.parse")
def test_fetch_reddit_articles(mock_feed_parse, mock_requests_get):
    """Test fetching articles from Reddit."""
    mock_requests_get.return_value.text = "mocked response"

    mock_entry = MagicMock()
    mock_entry.title = "Reddit DevOps Post"
    mock_entry.link = "https://reddit.com/1"
    mock_entry.get = MagicMock(
        side_effect=lambda key, default="": (
            "<div>Reddit content</div>" if key in ("summary", "description") else default
        )
    )

    mock_feed_parse.return_value.entries = [mock_entry]

    articles = fetch_reddit_articles()
    assert articles[0]["title"] == "Reddit DevOps Post"
    assert articles[0]["source"] == "Reddit"
    assert "summary" in articles[0]


# -------------------------------------
# fetch_tech_blog_articles
# -------------------------------------
@patch("digesting_feed.fetcher.feedparser.parse")
def test_fetch_tech_blog_articles(mock_parse):
    """Test fetching articles from tech blogs."""
    mock_entry = MagicMock()
    mock_entry.title = "New Tech Post"
    mock_entry.link = "https://blog.com/1"
    mock_entry.get = MagicMock(
        side_effect=lambda key, default="": (
            "<p>Tech blog summary</p>"
            if key == "summary"
            else [{"value": "<p>Full content</p>"}] if key == "content" else default
        )
    )

    mock_parse.return_value.entries = [mock_entry]

    articles = fetch_tech_blog_articles()
    assert articles[0]["title"].startswith("[")
    assert articles[0]["source"] in ("Netflix", "Amazon AWS", "Google", "Microsoft")
    assert "summary" in articles[0]
