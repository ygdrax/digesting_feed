"""Module for managing historical archives of articles."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .helper import helper

# Constants
JSON_GLOB_PATTERN = "*.json"


class ArchiveManager:
    """Manages historical archives of articles by date."""
    
    def __init__(self, archive_dir: str = "data/archives"):
        self.archive_dir = archive_dir
        
    def archive_articles_by_date(self, articles: List[Dict]) -> None:
        """
        Archive articles by grouping them by date.
        
        Args:
            articles: List of articles to archive
        """
        # Group articles by date
        articles_by_date = {}
        for article in articles:
            date = article.get("date")
            if date:
                if date not in articles_by_date:
                    articles_by_date[date] = []
                articles_by_date[date].append(article)
        
        # Save each date's articles to separate files
        for date, date_articles in articles_by_date.items():
            self._save_daily_archive(date, date_articles)
    
    def _save_daily_archive(self, date: str, articles: List[Dict]) -> None:
        """
        Save articles for a specific date to archive.
        Only saves if archive doesn't exist (once per day).
        
        Args:
            date: Date string in YYYY-MM-DD format
            articles: List of articles for that date (already top 25)
        """
        archive_path = helper.get_full_path(f"{self.archive_dir}/{date}.json", must_exist=False)
        Path(archive_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Only save if archive doesn't exist for this date (once per day)
        if Path(archive_path).exists():
            return  # Don't overwrite existing daily archive
        
        # Sort by score (highest first) and save
        articles.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        with open(archive_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
    
    def get_archived_articles(self, date: Optional[str] = None) -> List[Dict]:
        """
        Get archived articles for a specific date or all dates.
        
        Args:
            date: Date string in YYYY-MM-DD format, or None for all dates
            
        Returns:
            List of articles
        """
        if date:
            return self._load_daily_archive(date)
        
        # Load all archived articles
        all_articles = []
        archive_dir_path = helper.get_full_path(self.archive_dir, must_exist=False)
        
        if not Path(archive_dir_path).exists():
            return []
        
        for archive_file in Path(archive_dir_path).glob(JSON_GLOB_PATTERN):
            try:
                with open(archive_file, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                    all_articles.extend(articles)
            except (json.JSONDecodeError, IOError):
                continue
        
        return all_articles
    
    def _load_daily_archive(self, date: str) -> List[Dict]:
        """
        Load archived articles for a specific date.
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            List of articles for that date
        """
        archive_path = helper.get_full_path(f"{self.archive_dir}/{date}.json", must_exist=False)
        
        if not Path(archive_path).exists():
            return []
        
        try:
            with open(archive_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def get_available_dates(self) -> List[str]:
        """
        Get list of available archive dates.
        
        Returns:
            Sorted list of date strings
        """
        archive_dir_path = helper.get_full_path(self.archive_dir, must_exist=False)
        
        if not Path(archive_dir_path).exists():
            return []
        
        dates = []
        for archive_file in Path(archive_dir_path).glob(JSON_GLOB_PATTERN):
            date = archive_file.stem
            try:
                # Validate date format
                datetime.strptime(date, "%Y-%m-%d")
                dates.append(date)
            except ValueError:
                continue
        
        return sorted(dates, reverse=True)  # Most recent first
    
    def cleanup_old_archives(self, retention_days: int = 14) -> None:
        """
        Clean up archive files older than retention period.
        
        Args:
            retention_days: Number of days to retain archives
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        archive_dir_path = helper.get_full_path(self.archive_dir, must_exist=False)
        
        if not Path(archive_dir_path).exists():
            return
        
        for archive_file in Path(archive_dir_path).glob(JSON_GLOB_PATTERN):
            try:
                file_date = datetime.strptime(archive_file.stem, "%Y-%m-%d")
                if file_date < cutoff_date:
                    archive_file.unlink()
                    print(f"Cleaned up old archive: {archive_file.name}")
            except (ValueError, OSError):
                continue
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about archived articles.
        
        Returns:
            Dictionary with archive statistics
        """
        available_dates = self.get_available_dates()
        total_articles = 0
        sources = set()
        
        for date in available_dates:
            articles = self._load_daily_archive(date)
            total_articles += len(articles)
            for article in articles:
                if 'source' in article:
                    sources.add(article['source'])
        
        return {
            'total_dates': len(available_dates),
            'total_articles': total_articles,
            'date_range': {
                'oldest': available_dates[-1] if available_dates else None,
                'newest': available_dates[0] if available_dates else None,
            },
            'sources': sorted(sources),
            'average_articles_per_day': total_articles / len(available_dates) if available_dates else 0
        }
    
    @staticmethod
    def _remove_duplicates_by_link(articles: List[Dict]) -> List[Dict]:
        """
        Remove duplicate articles based on their 'link' field.
        
        Args:
            articles: List of articles to deduplicate
            
        Returns:
            Deduplicated list of articles
        """
        seen = set()
        unique = []
        for article in articles:
            link = article.get("link")
            if link and link not in seen:
                seen.add(link)
                unique.append(article)
        return unique