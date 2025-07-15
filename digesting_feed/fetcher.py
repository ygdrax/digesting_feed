import re

import feedparser
import requests
from bs4 import BeautifulSoup

HN_URL = "https://hnrss.org/frontpage"
REDDIT_URLS = [
    "https://www.reddit.com/r/devops/.rss",
    "https://www.reddit.com/r/sysadmin/.rss",
]

TECH_BLOG_FEEDS = {
    "Netflix": "https://netflixtechblog.com/feed",
    "Amazon AWS": "https://aws.amazon.com/blogs/opensource/feed/",
    "Google": "https://opensource.googleblog.com/feeds/posts/default",
    "Microsoft": "https://techcommunity.microsoft.com/gxcuf89792/rss/2.0?board.id=AzureDevOps",
}


def clean_html(raw_html):
    text = BeautifulSoup(raw_html, "html.parser").get_text()
    return re.sub(r"\s+", " ", text).strip()[:300]


def fetch_hn_articles():
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
    articles = []
    headers = {"User-Agent": "digesting_feed"}
    for url in REDDIT_URLS:
        feed = feedparser.parse(requests.get(url, headers=headers, timeout=10).text)
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
