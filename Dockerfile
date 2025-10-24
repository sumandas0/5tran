# Use Python 3.11 base image
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies with uv (no dev dependencies, frozen lockfile)
RUN uv sync --frozen --no-dev --no-cache

# Copy application code
COPY app.py ./
COPY src/ ./src/

# Create directory for generated connectors
RUN mkdir -p src/connectors

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser


# Run the Gradio app with uv
CMD ["uv", "run", "python", "app.py"]

