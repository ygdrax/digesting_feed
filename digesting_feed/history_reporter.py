"""Module for generating historical reports and analytics."""

import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from jinja2 import Template

from .archive_manager import ArchiveManager
from .helper import helper


class HistoryReporter:
    """Generates historical reports and analytics."""
    
    def __init__(self, archive_manager: Optional[ArchiveManager] = None):
        self.archive_manager = archive_manager or ArchiveManager()
    
    def generate_historical_summary(self, days: int = 7) -> Dict:
        """
        Generate a summary of articles from the last N days.
        
        Args:
            days: Number of days to include in summary
            
        Returns:
            Dictionary with historical summary data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        # Get articles from the specified date range
        articles_by_date = {}
        date_range = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            date_range.append(date_str)
            articles = self.archive_manager.get_archived_articles(date_str)
            articles_by_date[date_str] = articles
        
        # Analyze trends
        daily_counts = {}
        source_trends = defaultdict(lambda: defaultdict(int))
        top_articles = []
        all_keywords = []
        
        for date_str, articles in articles_by_date.items():
            daily_counts[date_str] = len(articles)
            
            for article in articles:
                source = article.get('source', 'Unknown')
                source_trends[source][date_str] = source_trends[source].get(date_str, 0) + 1
                
                # Collect high-scoring articles
                score = article.get('score', 0)
                if score > 0:
                    top_articles.append({
                        'title': article.get('title', 'Untitled'),
                        'source': source,
                        'date': date_str,
                        'score': score,
                        'link': article.get('link', '#')
                    })
                
                # Extract keywords from titles for trend analysis
                title = article.get('title', '').lower()
                words = [word.strip('.,!?":;()[]{}') for word in title.split() 
                        if len(word) > 3 and word.isalpha()]
                all_keywords.extend(words)
        
        # Sort top articles by score
        top_articles.sort(key=lambda x: x['score'], reverse=True)
        
        # Get trending keywords
        keyword_counts = Counter(all_keywords)
        trending_keywords = keyword_counts.most_common(20)
        
        return {
            'date_range': {
                'start': date_range[0],
                'end': date_range[-1],
                'days': days
            },
            'daily_counts': daily_counts,
            'total_articles': sum(daily_counts.values()),
            'average_per_day': sum(daily_counts.values()) / days,
            'source_trends': dict(source_trends),
            'top_articles': top_articles[:20],  # Top 20 articles
            'trending_keywords': trending_keywords[:10],  # Top 10 keywords
            'sources_summary': self._get_sources_summary(articles_by_date)
        }
    
    def _get_sources_summary(self, articles_by_date: Dict[str, List[Dict]]) -> Dict:
        """Get summary statistics by source."""
        source_stats = defaultdict(lambda: {'total': 0, 'avg_score': 0, 'max_score': 0})
        
        for articles in articles_by_date.values():
            for article in articles:
                source = article.get('source', 'Unknown')
                score = article.get('score', 0)
                
                source_stats[source]['total'] += 1
                source_stats[source]['avg_score'] += score
                source_stats[source]['max_score'] = max(source_stats[source]['max_score'], score)
        
        # Calculate averages
        for source_data in source_stats.values():
            if source_data['total'] > 0:
                source_data['avg_score'] = round(source_data['avg_score'] / source_data['total'], 2)
        
        return dict(source_stats)
    
    def generate_html_report(self, days: int = 7, output_file: str = "history_report.html") -> None:
        """
        Generate an HTML report of historical data.
        
        Args:
            days: Number of days to include in report
            output_file: Output HTML file path
        """
        summary = self.generate_historical_summary(days)
        
        template_str = self._get_report_template()
        template = Template(template_str)
        
        rendered = template.render(
            summary=summary,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(rendered)
        
        print(f"Historical report generated: {output_file}")
    
    def _get_report_template(self) -> str:
        """Get the HTML template for historical reports."""
        return '''<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <title>📊 DevOps Digest - Historical Report</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }
        .metric-card {
            background-color: #1e1e1e;
            border: 1px solid #2a2a2a;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #58a6ff;
        }
        .keyword-tag {
            display: inline-block;
            background-color: #2a2a2a;
            color: #e0e0e0;
            padding: 4px 8px;
            margin: 2px;
            border-radius: 4px;
            font-size: 0.8em;
        }
        .source-badge {
            background-color: #444;
            color: #fff;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.7em;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <h1 class="mb-4 text-center">📊 DevOps Digest - Historical Report</h1>
        <p class="text-center text-muted">
            Analysis for {{ summary.date_range.start }} to {{ summary.date_range.end }} 
            ({{ summary.date_range.days }} days)
        </p>
        <p class="text-center text-muted small">Generated at {{ generated_at }}</p>

        <!-- Key Metrics -->
        <div class="row">
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{{ summary.total_articles }}</div>
                    <div>Total Articles</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{{ "%.1f"|format(summary.average_per_day) }}</div>
                    <div>Articles/Day</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{{ summary.sources_summary | length }}</div>
                    <div>Sources</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <div class="metric-value">{{ summary.date_range.days }}</div>
                    <div>Days Analyzed</div>
                </div>
            </div>
        </div>

        <!-- Daily Activity Chart -->
        <div class="metric-card">
            <h3>📈 Daily Article Count</h3>
            <div class="chart-container">
                <canvas id="dailyChart"></canvas>
            </div>
        </div>

        <!-- Source Distribution -->
        <div class="metric-card">
            <h3>📡 Source Distribution</h3>
            <div class="row">
                {% for source, stats in summary.sources_summary.items() %}
                <div class="col-md-4 mb-3">
                    <strong>{{ source }}</strong>
                    <div class="text-muted small">
                        {{ stats.total }} articles | Avg score: {{ stats.avg_score }} | Max: {{ stats.max_score }}
                    </div>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar" role="progressbar" 
                             style="width: {{ (stats.total / summary.total_articles * 100) | round }}%">
                            {{ (stats.total / summary.total_articles * 100) | round }}%
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Top Articles -->
        <div class="metric-card">
            <h3>🏆 Top Articles by Score</h3>
            <div class="list-group">
                {% for article in summary.top_articles[:10] %}
                <div class="list-group-item bg-dark border-secondary">
                    <a href="{{ article.link }}" target="_blank" class="text-decoration-none">
                        <strong>{{ article.title }}</strong>
                    </a>
                    <div class="d-flex justify-content-between align-items-center mt-1">
                        <small class="text-muted">
                            <span class="source-badge">{{ article.source }}</span>
                            {{ article.date }}
                        </small>
                        <span class="badge bg-primary">Score: {{ article.score }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Trending Keywords -->
        <div class="metric-card">
            <h3>🔥 Trending Keywords</h3>
            <div>
                {% for keyword, count in summary.trending_keywords %}
                <span class="keyword-tag">
                    {{ keyword }} <small>({{ count }})</small>
                </span>
                {% endfor %}
            </div>
        </div>

        <footer class="mt-5 text-center text-muted">
            <small>Generated by <strong>digesting_feed</strong> historical reporter.</small>
        </footer>
    </div>

    <script>
        // Daily Activity Chart
        const ctx = document.getElementById('dailyChart').getContext('2d');
        const dailyData = {{ summary.daily_counts | tojson }};
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: Object.keys(dailyData),
                datasets: [{
                    label: 'Articles per Day',
                    data: Object.values(dailyData),
                    borderColor: '#58a6ff',
                    backgroundColor: 'rgba(88, 166, 255, 0.1)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#e0e0e0'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#e0e0e0'
                        },
                        grid: {
                            color: '#2a2a2a'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#e0e0e0'
                        },
                        grid: {
                            color: '#2a2a2a'
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>'''
    
    def export_data(self, output_file: str = "historical_data.json", days: int = 30) -> None:
        """
        Export historical data to JSON format.
        
        Args:
            output_file: Output JSON file path
            days: Number of days to export
        """
        summary = self.generate_historical_summary(days)
        
        # Get all articles for the period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        all_articles = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            articles = self.archive_manager.get_archived_articles(date_str)
            all_articles.extend(articles)
        
        export_data = {
            'export_info': {
                'generated_at': datetime.now().isoformat(),
                'date_range': summary['date_range'],
                'total_articles': len(all_articles)
            },
            'summary': summary,
            'articles': all_articles
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"Historical data exported: {output_file}")