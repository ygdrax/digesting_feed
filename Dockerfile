FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml .

# Install dependencies with uv
RUN uv pip install . --system

# Copy the rest of the application
COPY . .

# Set the entry point
CMD ["python", "-m", "digesting_feed.main"]
    