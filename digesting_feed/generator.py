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

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def summarize_text(text, sentence_count=2):
    """Summarize the given text using simple sentence extraction."""
    if not text or len(text.strip()) < 50:
        return text
    
    # Clean the text
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Simple sentence splitting (works for most cases)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if len(sentences) <= sentence_count:
        return text
    
    # Simple scoring: prefer sentences with more words and common keywords
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        words = sentence.lower().split()
        # Score based on length (prefer medium-length sentences)
        length_score = min(len(words) / 20.0, 1.0) if len(words) > 5 else 0.1
        
        # Score based on position (prefer earlier sentences)
        position_score = 1.0 - (i / len(sentences)) * 0.3
        
        # Score based on keywords that might indicate importance
        keyword_score = 0
        important_words = ['key', 'important', 'significant', 'major', 'critical', 
                          'new', 'latest', 'update', 'release', 'announce']
        for word in important_words:
            if word in sentence.lower():
                keyword_score += 0.1
        
        total_score = length_score + position_score + keyword_score
        scored_sentences.append((sentence, total_score))
    
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
    
    return '. '.join(result_sentences) + '.' if result_sentences else text[:200] + '...'


def generate_html(articles, output_file="index.html"):
    """Get static HTML and render articles using a Jinja2 template and writes to default file."""
    # Summarize each article's summary (or content if available)
    template_str = load_template_from_file()

    for article in articles:
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
    rendered = template.render(articles=articles)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered)
