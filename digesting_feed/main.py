"""digesting_feed.main"""
from .fetcher import fetch_hn_articles, fetch_reddit_articles, fetch_tech_blog_articles
from .generator import generate_html
from .configfile import keywords, source_weights

def score_article(article):
    """
    Calculate a relevance score for a given article based on the presence of 
    specific keywords in the title and the weighted importance of the source.

    Args:
        article (dict): A dictionary representing an article. Expected keys include
            "title" (str) and "source" (str).

    Returns:
        int: The calculated score, which is the sum of matched keywords and the source weight.
    """
    title = article["title"].lower()
    score = sum(1 for kw in keywords if kw in title)
    score += source_weights.get(article["source"], 0)
    return score

def main():
    """
    Fetch articles from multiple sources, score them based on relevance,
    select the top 20 scoring articles, and generate an HTML output.

    This function serves as the main entry point for the script.
    """
    articles = (
        fetch_hn_articles()
        + fetch_reddit_articles()
        + fetch_tech_blog_articles()
    )
    for article in articles:
        article["score"] = score_article(article)
    top_articles = sorted(articles, key=lambda x: x["score"], reverse=True)[:20]
    generate_html(top_articles)

if __name__ == "__main__":
    main()
