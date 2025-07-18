"""Main module to fetch, score, save, and generate daily devops digest articles."""

from datetime import datetime
import requests
from digesting_feed import manage_article
from digesting_feed.helper import env
from digesting_feed.fetcher import (
    fetch_hn_articles,
    fetch_reddit_articles,
    fetch_tech_blog_articles,
)
from digesting_feed.generator import generate_html


def score_article(article):
    """Score an article based on its title and source."""
    title = article["title"].lower()
    keywords = env.load_json_env("KEYWORDS", {})
    score = sum(1 for kw in keywords if kw in title)
    score += env.load_json_env("SOURCE_WEIGHTS", {}).get(article["source"], 0)
    return score


def main():
    """Main function to fetch articles, merge with saved, score,
    add date, save, generate HTML."""

    # Fetch fresh articles
    fresh_articles = []

    try:
        fresh_articles.extend(fetch_hn_articles())
    except requests.RequestException as e:
        print(f"Failed to fetch Hacker News articles: {e}")

    try:
        fresh_articles.extend(fetch_reddit_articles())
    except requests.RequestException as e:
        print(f"Failed to fetch Reddit articles: {e}")

    try:
        fresh_articles.extend(fetch_tech_blog_articles())
    except requests.RequestException as e:
        print(f"Failed to fetch tech blog articles: {e}")

    # Load previously saved articles
    try:
        old_articles = manage_article.load_articles_from_json()
    except FileNotFoundError:
        print("No existing articles found, starting fresh.")
        old_articles = []
    except (OSError, IOError) as e:
        print(f"Failed to load existing articles: {e}")
        old_articles = []

    # Combine fresh and old articles
    combined_articles = fresh_articles + old_articles

    # Deduplicate by 'link', keep first occurrence
    seen_links = set()
    unique_articles = []
    for article in combined_articles:
        if article["link"] not in seen_links:
            seen_links.add(article["link"])
            unique_articles.append(article)

    today_str = datetime.now().strftime("%Y-%m-%d")

    # Score all articles and add date if missing
    for article in unique_articles:
        article["score"] = score_article(article)
        if "date" not in article:
            article["date"] = today_str

    # Save all unique articles (not limited to top 20)
    manage_article.save_articles_to_json(unique_articles)

    # Generate HTML for all articles
    generate_html(unique_articles)


if __name__ == "__main__":
    main()
