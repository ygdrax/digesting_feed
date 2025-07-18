"""Module for generating HTML from articles with summarization."""

from jinja2 import Template
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
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
    """Summarize the given text using LSA summarization."""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary)


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
