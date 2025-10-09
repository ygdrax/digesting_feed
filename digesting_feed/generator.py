"""Module for generating HTML from articles with summarization."""

import re

from jinja2 import Template

from digesting_feed.helper import helper


def load_template_from_file(relative_path="static/template.html") -> str:
    """
    Load and return the contents of a template HTML file.

    Args:
        relative_path (str): Relative path to the HTML template.

    Returns:
        str: The contents of the template file as a string.

    Raises:
        FileNotFoundError: If the template file does not exist.
    """
    full_path = helper.get_full_path(relative_path)

    with open(full_path, encoding="utf-8") as f:
        return f.read()


def _score_sentence(sentence, position, total_sentences):
    """Score a sentence based on various factors."""
    words = sentence.lower().split()
    
    # Length score - prefer concise, impactful sentences
    word_count = len(words)
    if 8 <= word_count <= 20:
        length_score = 1.0
    elif 5 <= word_count <= 30:
        length_score = 0.8
    elif word_count < 5:
        length_score = 0.1
    else:
        length_score = 0.3
    
    # Position score (prefer earlier sentences but not too heavily)
    position_score = 1.0 - (position / total_sentences) * 0.15
    
    # Enhanced keyword scoring for DevOps/tech content
    tech_keywords = ['kubernetes', 'docker', 'aws', 'cloud', 'devops', 'infrastructure',
                     'container', 'microservices', 'api', 'service', 'application', 'deployment',
                     'security', 'monitoring', 'observability', 'platform', 'ci/cd', 'automation',
                     'scalability', 'performance', 'orchestration', 'helm', 'terraform']
    
    important_words = ['key', 'important', 'significant', 'critical', 'essential', 'crucial',
                       'new', 'latest', 'introduce', 'announcement', 'release', 'update',
                       'solution', 'problem', 'issue', 'challenge', 'feature', 'improvement',
                       'enables', 'addresses', 'provides', 'allows', 'helps']
    
    # Action/insight words that indicate valuable content
    insight_words = ['because', 'however', 'therefore', 'enables', 'addresses', 'solves',
                     'improves', 'reduces', 'increases', 'provides', 'allows', 'prevents']
    
    keyword_score = 0
    sentence_lower = sentence.lower()
    
    # Higher weight for tech keywords
    for word in tech_keywords:
        if word in sentence_lower:
            keyword_score += 0.2
    
    # Medium weight for important words
    for word in important_words:
        if word in sentence_lower:
            keyword_score += 0.15
    
    # Bonus for insight words (shows cause/effect, solutions)
    for word in insight_words:
        if word in sentence_lower:
            keyword_score += 0.1
    
    return length_score + position_score + keyword_score


def summarize_text(text, sentence_count=2):
    """Summarize the given text using simple sentence extraction."""
    if not text or len(text.strip()) < 50:
        return text

    # Clean the text
    text = re.sub(r'\s+', ' ', text.strip())
    
    # If text is already reasonably short, return as is
    if len(text) <= 300:
        return text

    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]

    if len(sentences) <= sentence_count:
        return text

    # Score sentences
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = _score_sentence(sentence, i, len(sentences))
        scored_sentences.append((sentence, score))

    # Sort by score and take top sentences
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    top_sentences = [s[0] for s in scored_sentences[:sentence_count]]

    # Return in original order
    result_sentences = []
    for sentence in sentences:
        if sentence in top_sentences:
            result_sentences.append(sentence)
            if len(result_sentences) >= sentence_count:
                break

    summary = '. '.join(result_sentences)
    if summary and not summary.endswith('.'):
        summary += '.'
    
    # If summary is too long, try to truncate at sentence boundary
    if len(summary) > 300:
        # Find the last complete sentence within 300 characters
        sentences_in_summary = summary.split('. ')
        truncated_summary = ''
        for sentence in sentences_in_summary:
            test_summary = truncated_summary + sentence + '. ' if truncated_summary else sentence + '. '
            if len(test_summary.strip()) <= 300:
                truncated_summary = test_summary.strip()
            else:
                break
        
        if truncated_summary:
            summary = truncated_summary
        else:
            # If even the first sentence is too long, truncate it properly
            first_sentence = sentences_in_summary[0]
            if len(first_sentence) > 297:
                summary = first_sentence[:297] + '...'
            else:
                summary = first_sentence + '.'
        
    return summary if summary else text[:200] + '...'


def generate_html(articles, output_file="index.html", max_articles=25):
    """Get static HTML and render articles using a Jinja2 template and writes to default file."""
    # Sort articles by date (newest first) and then by score (highest first)
    sorted_articles = sorted(articles, key=lambda x: (x.get('date', ''), -x.get('score', 0)), reverse=True)
    
    # Limit to top articles only
    sorted_articles = sorted_articles[:max_articles]
    
    # Summarize each article's summary (or content if available)
    template_str = load_template_from_file()

    for article in sorted_articles:
        text = article.get("summary") or article.get("content") or article.get("title")
        if text and len(text.split()) > 20:  # Only summarize if text is long enough
            try:
                summary = summarize_text(text)
                article["summary"] = summary
            except ValueError:
                pass
            except Exception as e:
                print(f"Unexpected error summarizing article: {e}")
                raise

    template = Template(template_str)
    rendered = template.render(
        articles=sorted_articles,
        generated_at=helper.get_current_timestamp(),
        total_articles=len(sorted_articles)
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered)
    
    print(f"Generated HTML with {len(sorted_articles)} articles: {output_file}")


def generate_daily_html(articles, output_file, date_str):
    """Generate HTML for a specific day's articles."""
    template_str = load_template_from_file()
    
    # Summarize articles if needed
    for article in articles:
        text = article.get("summary") or article.get("content") or article.get("title")
        if text and len(text.split()) > 20:
            try:
                summary = summarize_text(text)
                article["summary"] = summary
            except Exception as e:
                print(f"Error summarizing article: {e}")
    
    # Sort by score
    articles.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    from datetime import datetime
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%B %d, %Y")
    
    template = Template(template_str)
    rendered = template.render(
        articles=articles,
        generated_at=helper.get_current_timestamp(),
        total_articles=len(articles),
        page_title=f"DevOps Digest - {formatted_date}",
        is_daily_archive=True,
        archive_date=formatted_date
    )
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered)
    
    print(f"Generated daily HTML: {output_file}")


def generate_archive_index(archive_manager, output_file="archives.html"):
    """Generate an index page for browsing historical archives."""
    from .archive_manager import ArchiveManager
    
    if not archive_manager:
        archive_manager = ArchiveManager()
    
    available_dates = archive_manager.get_available_dates()
    stats = archive_manager.get_statistics()
    
    # Group dates by month for better organization
    dates_by_month = {}
    for date in available_dates:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            month_key = date_obj.strftime("%Y-%m")
            if month_key not in dates_by_month:
                dates_by_month[month_key] = []
            
            # Get article count for this date
            articles = archive_manager.get_archived_articles(date)
            dates_by_month[month_key].append({
                'date': date,
                'count': len(articles),
                'display_date': date_obj.strftime("%B %d, %Y")
            })
        except ValueError:
            continue
    
    # Sort months and dates
    for month_data in dates_by_month.values():
        month_data.sort(key=lambda x: x['date'], reverse=True)
    
    template_str = _get_archive_index_template()
    template = Template(template_str)
    
    rendered = template.render(
        dates_by_month=dates_by_month,
        stats=stats,
        generated_at=helper.get_current_timestamp()
    )
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered)
    
    print(f"Generated archive index: {output_file}")


def _get_archive_index_template():
    """Get template for archive index page."""
    return '''<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <title>📚 DevOps Digest - Archives</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .archive-card {
            background-color: #1e1e1e;
            border: 1px solid #2a2a2a;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
        }
        .date-link {
            color: #58a6ff;
            text-decoration: none;
        }
        .date-link:hover {
            color: #1f6feb;
            text-decoration: underline;
        }
        .article-count {
            background-color: #444;
            color: #fff;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <h1 class="mb-4 text-center">📚 DevOps Digest - Archives</h1>
        <p class="text-center text-muted">Browse historical articles by date</p>
        
        <!-- Statistics -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="archive-card text-center">
                    <h4>{{ stats.total_articles }}</h4>
                    <small class="text-muted">Total Articles</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="archive-card text-center">
                    <h4>{{ stats.total_dates }}</h4>
                    <small class="text-muted">Archive Days</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="archive-card text-center">
                    <h4>{{ "%.1f"|format(stats.average_articles_per_day) }}</h4>
                    <small class="text-muted">Avg/Day</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="archive-card text-center">
                    <h4>{{ stats.sources | length }}</h4>
                    <small class="text-muted">Sources</small>
                </div>
            </div>
        </div>
        
        <!-- Navigation -->
        <div class="mb-3 text-center">
            <a href="index.html" class="btn btn-primary me-2">📊 Current Digest</a>
            <a href="history_report.html" class="btn btn-outline-secondary">📈 Historical Report</a>
        </div>
        
        <!-- Archive Dates by Month -->
        {% for month, dates in dates_by_month.items() %}
        <div class="archive-card">
            <h3>{{ month }}</h3>
            <div class="row">
                {% for date_info in dates %}
                <div class="col-md-6 mb-3">
                    <div class="d-flex justify-content-between align-items-center p-2 border rounded">
                        <div>
                            <a href="daily_{{ date_info.date }}.html" class="date-link fw-bold">
                                📊 {{ date_info.display_date }}
                            </a>
                            <br>
                            <small class="text-muted">Daily DevOps Digest</small>
                        </div>
                        <span class="article-count">{{ date_info.count }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% else %}
        <div class="archive-card text-center">
            <p class="text-muted">No archives available yet.</p>
        </div>
        {% endfor %}
        
        <footer class="mt-5 text-center text-muted">
            <small>Generated at {{ generated_at }} by <strong>digesting_feed</strong></small>
        </footer>
    </div>
</body>
</html>'''
