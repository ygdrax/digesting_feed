from .fetcher import fetch_hn_articles, fetch_reddit_articles, fetch_tech_blog_articles
from .generator import generate_html

def score_article(article):
    title = article["title"].lower()
    keywords = ["devops", "cloud", "kubernetes", "observability", "ai", "infra", "platform", "reliability", "linux", "docker", "automation", "monitoring", "security", "scalability", "performance", "networking"]
    score = sum(1 for kw in keywords if kw in title)

    source_weights = {
        "Netflix": 2,
        "Amazon AWS": 2,
        "Google": 2,
        "Microsoft": 2,
        "Hacker News": 5,
        "Reddit": 5
    }
    score += source_weights.get(article["source"], 0)
    return score

def main():
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
