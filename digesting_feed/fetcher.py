"""digesting_feed.fetcher
"""
import re
import requests
import feedparser
from bs4 import BeautifulSoup
from .configfile import HN_URL, REDDIT_URLS, TECH_BLOG_FEEDS


def clean_html(raw_html):
    """
    Remove HTML tags and extra whitespace from a raw HTML string,
    returning the first 300 characters of clean text.

    Args:
        raw_html (str): A string containing HTML content.

    Returns:
        str: Cleaned and truncated plain text.
    """
    text = BeautifulSoup(raw_html, "html.parser").get_text()
    return re.sub(r"\s+", " ", text).strip()[:300]


def fetch_hn_articles():
    """
    Fetch articles from the Hacker News front page RSS feed.

    Returns:
        list of dict: A list of article dictionaries with keys:
            "title", "link", "source", "summary", and "score".
    """
    feed = feedparser.parse(HN_URL)
    return [
        {
            "title": entry.title,
            "link": entry.link,
            "source": "Hacker News",
            "summary": clean_html(entry.get("summary", "")),
            "score": 0,
        }
        for entry in feed.entries
    ]


def fetch_reddit_articles():
    """
    Fetch articles from specified Reddit RSS feeds.

    Returns:
        list of dict: A list of article dictionaries with keys:
            "title", "link", "source", "summary", and "score".
    """
    articles = []
    headers = {"User-Agent": "digesting_feed"}
    for url in REDDIT_URLS:
        response = requests.get(url, headers=headers, timeout=10)
        feed = feedparser.parse(response.text)
        for entry in feed.entries:
            summary = entry.get("summary", "") or entry.get("description", "")
            articles.append(
                {
                    "title": entry.title,
                    "link": entry.link,
                    "source": "Reddit",
                    "summary": clean_html(summary),
                    "score": 0,
                }
            )
    return articles


def fetch_tech_blog_articles():
    """
    Fetch articles from configured tech blog RSS feeds, limiting
    to the latest 5 entries per feed.

    Returns:
        list of dict: A list of article dictionaries with keys:
            "title", "link", "source", "summary", and "score".
    """
    articles = []
    for name, url in TECH_BLOG_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            summary = entry.get("summary", "") or entry.get("content", [{}])[0].get(
                "value", ""
            )
            articles.append(
                {
                    "title": f"[{name}] {entry.title}",
                    "link": entry.link,
                    "source": name,
                    "summary": clean_html(summary),
                    "score": 0,
                }
            )
    return articles
