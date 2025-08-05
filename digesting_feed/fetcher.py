"""Module for fetching articles from various sources like Hacker News, Reddit, and tech blogs."""

import re

import feedparser
import requests
from bs4 import BeautifulSoup

from digesting_feed.helper import env

HN_URL = env.get_env_var("HN_URL", default=None)

REDDIT_URLS = env.load_json_env("REDDIT_URLS", {})

TECH_BLOG_FEEDS = env.load_json_env("TECH_BLOG_FEEDS", {})


def clean_html(raw_html):
    """Sanitize HTML content to extract text and limit length."""
    text = BeautifulSoup(raw_html, "html.parser").get_text()
    return re.sub(r"\s+", " ", text).strip()[:300]


def fetch_hn_articles():
    """Fetch articles from Hacker News RSS feed."""
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
    """Fetch articles from Reddit feeds."""
    articles = []
    headers = {"User-Agent": "digesting_feed"}
    for url in REDDIT_URLS:
        response = requests.get(url, headers=headers, timeout=10)  # <-- added timeout
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
    """Fetch articles from various tech blogs."""
    articles = []
    for name, url in TECH_BLOG_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            summary = entry.get("summary", "") or entry.get("content", [{}])[0].get("value", "")
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
