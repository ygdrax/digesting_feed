# Digesting_feed

More and more I feel I don't have enought time to read all the articles I want. I wanted a way to get the most important ones from multiple sources updated everyday for me. So this is it.

## Quick Start

```bash
pip install uv
uv venv .venv
source .venv/bin/activate

uv pip install -r requirements.txt

python -m digesting_feed.main
```

## Development

### Run Pre-Commit Hooks

```bash
pre-commit install
pre-commit clean
pre-commit run --all-files
```

## Notes

- The file `digesting_feed/data/articles.json` is ignored by git and used for storing fetched articles.
- If you add new dependencies, use `uv pip install <package>` to keep your environment up to date.

---
