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
    """Sanitize HTML content to extract text with better formatting."""
    if not raw_html:
        return ""
    
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # Remove script and style elements completely
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text and clean up
    text = soup.get_text()
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Clean up common HTML artifacts
    text = re.sub(r'\[[^\]]*\]', '', text)  # Remove [CDATA] and similar
    text = re.sub(r'&#\d+;', ' ', text)  # Remove HTML entities
    
    return text.strip()


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


def _extract_entry_summary(entry):
    """Extract summary content from a feed entry, preferring full content over description."""
    # Try to get the full content first (usually in content:encoded)
    if hasattr(entry, 'content') and entry.content:
        if isinstance(entry.content, list) and len(entry.content) > 0:
            content_value = entry.content[0].get('value', '')
            if content_value and len(content_value) > 200:  # Prefer if substantial content
                return content_value
        elif hasattr(entry.content, 'value'):
            return entry.content.value
        elif len(str(entry.content)) > 200:
            return str(entry.content)
    
    # Fallback to summary (often has more content than description)
    if hasattr(entry, 'summary') and entry.summary and len(entry.summary) > 100:
        return entry.summary
    
    # Last resort: description (often truncated)
    if hasattr(entry, 'description'):
        return entry.description
    
    return ""


def _process_feed_entries(feed, source_name):
    """Process entries from a feed source."""
    articles = []
    for entry in feed.entries[:5]:  # Limit to top 5 per source
        try:
            if not entry.title or not entry.link:
                continue
                
            summary = _extract_entry_summary(entry)
            articles.append({
                "title": f"[{source_name}] {entry.title}",
                "link": entry.link,
                "source": source_name,
                "summary": clean_html(summary),
                "score": 0,
            })
        except Exception as e:
            print(f"Error processing entry from {source_name}: {e}")
            continue
    return articles


def _report_failed_sources(failed_sources):
    """Report sources that failed to fetch."""
    if not failed_sources:
        return
        
    print(f"Failed to fetch from {len(failed_sources)} sources:")
    for failure in failed_sources[:10]:  # Show first 10 failures
        print(f"  - {failure}")
    if len(failed_sources) > 10:
        print(f"  ... and {len(failed_sources) - 10} more")


def fetch_tech_blog_articles():
    """Fetch articles from various tech blogs with improved error handling."""
    articles = []
    failed_sources = []
    
    for name, url in TECH_BLOG_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            
            # Check if feed was parsed successfully
            if hasattr(feed, 'bozo') and feed.bozo and not feed.entries:
                failed_sources.append(f"{name}: Feed parsing failed")
                continue
                
            feed_articles = _process_feed_entries(feed, name)
            articles.extend(feed_articles)
                    
        except Exception as e:
            failed_sources.append(f"{name}: {str(e)}")
            continue
    
    _report_failed_sources(failed_sources)
    
    successful_sources = len(TECH_BLOG_FEEDS) - len(failed_sources)
    print(f"Successfully fetched {len(articles)} articles from {successful_sources} tech blog sources")
    return articles
