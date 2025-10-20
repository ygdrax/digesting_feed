"""Main module to fetch, score, save, and generate daily devops digest articles."""

from datetime import datetime
from typing import List, Dict

import requests

from digesting_feed import manage_article
from digesting_feed.archive_manager import ArchiveManager
from digesting_feed.fetcher import (
    fetch_hn_articles,
    fetch_reddit_articles,
    fetch_tech_blog_articles,
)
from digesting_feed.generator import generate_html, generate_archive_index
from digesting_feed.helper import env


def score_article(article: Dict) -> int:
    """Score an article based on its title, source, and recency."""
    title = article["title"].lower()
    keywords = env.load_json_env("KEYWORDS", [])
    
    # Base score from keyword matching (double weight for keyword matches)
    keyword_score = sum(2 for kw in keywords if kw in title)
    
    # Source weight
    source_score = env.load_json_env("SOURCE_WEIGHTS", {}).get(article["source"], 0)
    
    # Recency bonus - prefer articles from today
    recency_bonus = 0
    today_str = datetime.now().strftime("%Y-%m-%d")
    if article.get("date") == today_str:
        recency_bonus = 3  # Significant bonus for fresh content
    
    return keyword_score + source_score + recency_bonus


def fetch_all_articles() -> List[Dict]:
    """Fetch articles from all sources with error handling."""
    fresh_articles = []
    
    fetchers = [
        ("Hacker News", fetch_hn_articles),
        ("Reddit", fetch_reddit_articles),
        ("Tech Blogs", fetch_tech_blog_articles),
    ]
    
    for source_name, fetcher in fetchers:
        try:
            fresh_articles.extend(fetcher())
        except requests.RequestException as e:
            print(f"Failed to fetch {source_name} articles: {e}")
    
    return fresh_articles


def load_existing_articles(archive_manager: ArchiveManager) -> List[Dict]:
    """Load recent existing articles only (last 3 days for deduplication)."""
    articles = []
    
    # Load previously saved articles
    try:
        articles.extend(manage_article.load_articles_from_json())
    except FileNotFoundError:
        print("No existing articles found, starting fresh.")
    except OSError as e:
        print(f"Failed to load existing articles: {e}")
    
    # Load only recent archived articles (last 3 days for deduplication)
    try:
        from datetime import timedelta
        recent_dates = []
        today = datetime.now()
        for i in range(3):  # Only last 3 days
            date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            recent_dates.append(date_str)
        
        archived = []
        for date_str in recent_dates:
            day_articles = archive_manager.get_archived_articles(date_str)
            archived.extend(day_articles)
        
        articles.extend(archived)
        print(f"Loaded {len(archived)} recent archived articles for deduplication")
    except Exception as e:
        print(f"Failed to load archived articles: {e}")
    
    return articles


def deduplicate_articles(articles: List[Dict]) -> List[Dict]:
    """Remove duplicate articles based on link and title similarity."""
    seen_links = set()
    seen_titles = set()
    unique_articles = []
    
    # Sort by date (newest first) to prioritize recent articles
    sorted_articles = sorted(articles, key=lambda x: x.get('date', ''), reverse=True)
    
    for article in sorted_articles:
        link = article.get("link")
        title = article.get("title", "").lower().strip()
        
        # Skip if we've seen this link before
        if link and link in seen_links:
            continue
            
        # Skip if we've seen a very similar title (fuzzy match)
        title_words = set(title.split())
        is_duplicate = False
        
        for seen_title in seen_titles:
            seen_words = set(seen_title.split())
            # If 80% of words overlap, consider it a duplicate
            if len(title_words & seen_words) / max(len(title_words), len(seen_words), 1) > 0.8:
                is_duplicate = True
                break
        
        if not is_duplicate and link and title:
            seen_links.add(link)
            seen_titles.add(title)
            unique_articles.append(article)
    
    return unique_articles


def process_articles(articles: List[Dict]) -> List[Dict]:
    """Score articles and add missing dates."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    for article in articles:
        article["score"] = score_article(article)
        if "date" not in article:
            article["date"] = today_str
    
    return articles


def generate_reports(articles: List[Dict], archive_manager: ArchiveManager) -> None:
    """Generate all HTML reports."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Generate today's main digest (index.html shows ONLY today's articles)
    generate_html(articles, output_file="index.html", max_articles=25, date_filter=today_str)
    
    # Generate historical daily pages in archives/ directory
    import os
    os.makedirs("archives", exist_ok=True)
    
    # Generate daily pages for all available dates
    available_dates = archive_manager.get_available_dates()
    from digesting_feed.generator import generate_daily_html
    
    for date_str in available_dates:
        daily_articles = archive_manager.get_archived_articles(date_str)
        if daily_articles:
            output_file = f"archives/daily_{date_str}.html"
            generate_daily_html(daily_articles, output_file, date_str)
    
    try:
        generate_archive_index(archive_manager, "archives.html")
    except Exception as e:
        print(f"Failed to generate archive index: {e}")
    
    # Generate historical report
    try:
        from digesting_feed.history_reporter import HistoryReporter
        reporter = HistoryReporter(archive_manager)
        reporter.generate_html_report(days=14, output_file="history_report.html")
        print("Generated historical report: history_report.html")
    except Exception as e:
        print(f"Failed to generate historical report: {e}")


def cleanup_and_stats(archive_manager: ArchiveManager) -> None:
    """Clean up old archives and print statistics."""
    try:
        archive_manager.cleanup_old_archives(retention_days=14)
    except Exception as e:
        print(f"Failed to cleanup old archives: {e}")
    
    try:
        stats = archive_manager.get_statistics()
        print(f"Archive stats: {stats['total_articles']} articles across {stats['total_dates']} days")
        if stats['date_range']['oldest'] and stats['date_range']['newest']:
            print(f"Date range: {stats['date_range']['oldest']} to {stats['date_range']['newest']}")
    except Exception as e:
        print(f"Failed to get archive statistics: {e}")


def main():
    """Main function orchestrating the entire process."""
    archive_manager = ArchiveManager()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Check if we already have today's digest
    today_archive = archive_manager.get_archived_articles(today_str)
    if today_archive:
        print(f"Today's digest already exists with {len(today_archive)} articles")
        print("Generating HTML from existing daily archive...")
        generate_reports(today_archive, archive_manager)
        cleanup_and_stats(archive_manager)
        return
    
    # Fetch all fresh articles (no existing articles, we want fresh daily digest)
    print("Generating fresh daily digest...")
    fresh_articles = fetch_all_articles()
    
    # Load recent articles only for deduplication (avoid showing same articles as yesterday)
    existing_articles = load_existing_articles(archive_manager)
    
    # Deduplicate against recent articles
    all_articles = fresh_articles + existing_articles
    unique_articles = deduplicate_articles(all_articles)
    
    # Keep only the fresh articles (remove the existing ones we only used for deduplication)
    fresh_unique = [a for a in unique_articles if a in fresh_articles]
    
    # Process and score the fresh articles
    processed_articles = process_articles(fresh_unique)
    
    # Sort by score and take only top 25 for today's digest
    processed_articles.sort(key=lambda x: x.get('score', 0), reverse=True)
    daily_top_articles = processed_articles[:25]
    
    # Set today's date on all articles
    for article in daily_top_articles:
        article["date"] = today_str
    
    print(f"Selected top {len(daily_top_articles)} articles for today's digest")
    
    # Save today's top 25 to archive (only once per day)
    archive_manager.archive_articles_by_date(daily_top_articles)
    
    # Generate HTML from today's top articles
    generate_reports(daily_top_articles, archive_manager)
    
    # Cleanup and stats
    cleanup_and_stats(archive_manager)


if __name__ == "__main__":
    main()
