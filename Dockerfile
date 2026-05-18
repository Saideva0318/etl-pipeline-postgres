# ============================================================
# Dockerfile - ETL Pipeline PostgreSQL
# Production-ready containerized ETL pipeline
# Author: Saideva0318
# ============================================================

# --- Build Stage ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Production Stage ---
FROM python:3.11-slim AS production

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY sql/ ./sql/
COPY .env.example .env.example

# Create necessary directories
RUN mkdir -p data/raw data/processed logs

# Create non-root user for security
RUN groupadd -r etluser && useradd -r -g etluser etluser
RUN chown -R etluser:etluser /app
USER etluser

# Environment variables (overridden at runtime)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO

# Health check - verifies pipeline can import modules
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.extractor import CSVExtractor; print('healthy')" || exit 1

# Default command runs the full ETL pipeline
CMD ["python", "-m", "src.pipeline"]
