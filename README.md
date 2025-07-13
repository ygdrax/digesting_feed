# Digesting_feed

More and more I feel I don't have enought time to read all the articles I want. I wanted a way to get the most important ones from multiple sources updated everyday for me. So this is it.

```bash
pip install uv
uv venv .venv
source .venv/bin/activate

uv pip install .

python -c "import nltk; nltk.download(['punkt', 'punkt_tab', 'averaged_perceptron_tagger'])"

python -m digesting_feed.main
```