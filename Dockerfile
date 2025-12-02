FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

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
    tesseract-ocr poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

RUN python -m spacy download en_core_web_sm

RUN mkdir -p /app/staticfiles
RUN python manage.py collectstatic --noinput || echo "No static files to collect"

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health/ || exit 1

CMD exec gunicorn Careermate.wsgi:application \
    --bind 0.0.0.0:${PORT} \
    --workers 2 \
    --threads 4 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
