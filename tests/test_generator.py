"""Tests for the generator module."""

from unittest.mock import patch, mock_open, MagicMock
from digesting_feed.generator import (
    summarize_text,
    generate_html,
    load_template_from_file,
)


def test_summarize_text_short_input():
    """Test summarize_text with short input."""
    text = "DevOps automates software delivery."
    summary = summarize_text(text, sentence_count=1)
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_summarize_text_long_input():
    """Test summarize_text with longer input."""
    text = ("DevOps automates software delivery and enhances efficiency. "
            "It combines development and operations teams for faster deployment. "
            "This approach improves scalability and reduces time to market. "
            "Organizations benefit from continuous integration and delivery. "
            "The practice enables rapid response to customer feedback.")
    summary = summarize_text(text, sentence_count=2)
    assert isinstance(summary, str)
    assert len(summary) > 0
    # Summary should be shorter than original
    assert len(summary) < len(text)


@patch("digesting_feed.generator.helper.get_full_path", return_value="static/template.html")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="<html>{{ articles|length }}</html>",
)
def test_load_template_from_file(mock_file, _mock_get_path):
    """Test loading the HTML template from file."""
    result = load_template_from_file()
    assert "{{ articles|length }}" in result
    mock_file.assert_called_once_with("static/template.html", "r", encoding="utf-8")


@patch("digesting_feed.generator.summarize_text", autospec=True)
@patch("digesting_feed.generator.load_template_from_file")
@patch("builtins.open", new_callable=mock_open)
def test_generate_html(mock_file, mock_load_template, mock_summarize):
    """Test HTML generation with article summarization."""
    articles = [
        {
            "title": "Cloud infra scaling at Netflix",
            "link": "https://example.com",
            "source": "Netflix",
            # Long enough summary to trigger summarization (>20 words)
            "summary": " ".join(["word"] * 30),
        }
    ]

    mock_load_template.return_value = (
        "<html>{% for a in articles %}{{ a.title }} - {{ a.summary }}" "{% endfor %}</html>"
    )
    mock_summarize.return_value = "Short summary."

    generate_html(articles, output_file="index.html")

    mock_summarize.assert_called_once()
    mock_file.assert_called_with("index.html", "w", encoding="utf-8")

    handle = mock_file()
    written_content = "".join(call.args[0] for call in handle.write.call_args_list)
    assert "Cloud infra scaling at Netflix" in written_content
    assert "Short summary." in written_content
