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

# Generate historical report
python -m digesting_feed.cli report --days 7

# View archive statistics
python -m digesting_feed.cli stats
```

### Manual Setup

```bash
pip install uv
uv venv .venv
source .venv/bin/activate

uv pip install .

python -m digesting_feed.main
```

## Historical Features

The application now maintains a comprehensive history of articles with the following features:

### Archive Management
- **Daily Archives**: Articles are automatically archived by date in separate JSON files
- **Extended Retention**: Archives are kept for 30 days (configurable)
- **Deduplication**: Intelligent deduplication prevents duplicate articles across dates
- **Statistics**: Track article counts, sources, and trends over time

### Web Interface Enhancements
- **Date Navigation**: Browse articles by specific dates with previous/next navigation
- **Keyboard Shortcuts**: Use arrow keys for date navigation, 'T' for today
- **Enhanced Filtering**: Filter by date and source with article counts
- **Archive Index**: Dedicated page for browsing historical archives (`archives.html`)
- **Historical Reports**: Rich analytics and visualizations (`history_report.html`)

### CLI Tools

The application includes a powerful CLI for managing archives:

```bash
# Generate a 7-day historical report
python -m digesting_feed.cli report --days 7 --output report.html

# Show archive statistics
python -m digesting_feed.cli stats

# Export historical data to JSON
python -m digesting_feed.cli export --days 30 --output data.json

# List all available archive dates
python -m digesting_feed.cli list

# Clean up old archives (with dry-run option)
python -m digesting_feed.cli cleanup --retention 30 --dry-run
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
make ruff-fix     # Run ruff with auto-fix and formatting
make format       # Format code with black and ruff
make check        # Run all checks (lint, format check, test)
make clean        # Clean Python cache files and build artifacts
make clean-all    # Clean everything including virtual environment
```

### Code Quality Tools

This project uses several tools to maintain code quality:

- **Ruff**: Fast Python linter with auto-fix capabilities
- **Black**: Code formatter for consistent styling
- **Pylint**: Additional linting for code quality
- **Pre-commit**: Git hooks for automated checks

#### Ruff Configuration

Ruff is configured in `pyproject.toml` with comprehensive linting rules including:
- Pycodestyle (`E`, `W`)
- Pyflakes (`F`)
- Import sorting (`I`)
- Code complexity (`C901`)
- Modern Python practices (`UP`)
- Bug prevention (`B`)
- Code simplification (`SIM`)
- And many more...

To run ruff manually:
```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
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
