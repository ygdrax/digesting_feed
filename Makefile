# Makefile for Digesting Feed project

.PHONY: help install install-dev run clean clean-all test lint ruff-fix format check setup

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup       - Create virtual environment and install dependencies"
	@echo "  make install     - Install production dependencies"
	@echo "  make install-dev - Install development dependencies"
	@echo "  make run         - Run the digesting feed application"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linting (ruff and pylint)"
	@echo "  make ruff-fix    - Run ruff with auto-fix and formatting"
	@echo "  make format      - Format code with black and ruff"
	@echo "  make check       - Run all checks (lint, format check, test)"
	@echo "  make clean       - Clean Python cache files and build artifacts"
	@echo "  make clean-all   - Clean everything including virtual environment"

# Setup virtual environment and install dependencies
setup:
	@echo "Setting up virtual environment..."
	pip install uv
	uv venv .venv
	@echo "Installing dependencies..."
	uv pip install .
	@echo "Setup complete! Activate with: source .venv/bin/activate"

# Install production dependencies
install:
	@echo "Installing production dependencies..."
	uv pip install .

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	uv pip install -e ".[dev]"

# Run the application
run:
	@echo "Running digesting feed..."
	python -m digesting_feed.main

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/ -v

# Run linting
lint:
	@echo "Running ruff linter..."
	ruff check .
	@echo "Running pylint..."
	pylint digesting_feed/ tests/

# Run ruff with auto-fix
ruff-fix:
	@echo "Running ruff with auto-fix..."
	ruff check --fix .
	@echo "Running ruff formatter..."
	ruff format .

# Format code
format:
	@echo "Formatting code with black..."
	black .
	@echo "Formatting with ruff..."
	ruff format .
	@echo "Fixing imports and other issues with ruff..."
	ruff check --fix .

# Run all checks
check: lint test
	@echo "Running format check..."
	black --check .
	@echo "All checks completed!"

# Clean Python cache files and build artifacts
clean:
	@echo "Cleaning Python cache files and build artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/
	rm -rf dist/
	@echo "Cleanup complete!"

# Clean everything including virtual environment
clean-all: clean
	@echo "Removing virtual environment..."
	rm -rf .venv
	@echo "Complete cleanup finished!"
