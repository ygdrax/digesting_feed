# Digesting_feed

More and more I feel I don't have enought time to read all the articles I want. I wanted a way to get the most important ones from multiple sources updated everyday for me. So this is it.

## Quick Start

### Using Makefile (Recommended)

```bash
# Setup everything (virtual environment + dependencies)
make setup

# Activate virtual environment
source .venv/bin/activate

# Run the application
make run
```

### Manual Setup

```bash
pip install uv
uv venv .venv
source .venv/bin/activate

uv pip install .

python -m digesting_feed.main
```

## Development

### Available Make Commands

```bash
make help         # Show all available commands
make setup        # Create virtual environment and install dependencies
make install      # Install production dependencies
make install-dev  # Install development dependencies
make run          # Run the digesting feed application
make test         # Run tests
make lint         # Run linting (ruff and pylint)
make format       # Format code with black
make check        # Run all checks (lint, format check, test)
make clean        # Clean Python cache files and build artifacts
make clean-all    # Clean everything including virtual environment
```

### Run Pre-Commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Clean and run all hooks
make clean
pre-commit run --all-files

# Or manually
pre-commit clean
pre-commit run --all-files
```

## Notes

- The file `digesting_feed/data/articles.json` is ignored by git and used for storing fetched articles.
- If you add new dependencies, use `uv pip install <package>` to keep your environment up to date.
- Use `make clean` regularly to clean up Python cache files and build artifacts.
- Use `make clean-all` to completely reset your development environment.

---
