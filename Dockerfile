# Build stage - để build dependencies
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Cài đầy đủ dependencies cho build (layer này sẽ được cache)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    gfortran \
    libopenblas-dev liblapack-dev \
    libpq-dev \
    libjpeg-dev zlib1g-dev libtiff5-dev \
    libffi-dev libssl-dev pkg-config \
    curl ca-certificates wget git \
    rustc cargo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy ONLY requirements files - layer này chỉ thay đổi khi dependencies thay đổi
COPY pyproject.toml uv.lock ./

# Install dependencies - layer này được cache nếu pyproject.toml không đổi
RUN pip install --no-cache-dir uv && uv sync --frozen

# Download spacy model - layer này được cache
RUN /app/.venv/bin/python -m spacy download en_core_web_sm

# Runtime stage - image nhỏ hơn để deploy
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PATH="/app/.venv/bin:$PATH"

# Chỉ cài runtime dependencies (không cần compiler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libopenblas0 \
    libgomp1 \
    libjpeg62-turbo \
    zlib1g \
    libtiff5 \
    tesseract-ocr \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment từ builder (đã compiled)
COPY --from=builder /app/.venv /app/.venv

# Copy application code - chỉ layer này thay đổi khi code thay đổi
COPY . .

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Create user and set permissions
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health/ || exit 1

CMD ["sh", "-c", "exec gunicorn Careermate.wsgi:application --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 300 --access-logfile - --error-logfile - --log-level info"]
