FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=2 --threads=2 --timeout=180 --access-logfile=- --error-logfile=-"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        gettext \
        libharfbuzz-subset0 \
        libharfbuzz0b \
        libopenjp2-7 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN adduser --uid 5678 --disabled-password --gecos "" appuser \
    && mkdir -p /app/media /app/staticfiles \
    && chown -R appuser:appuser /app

COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

COPY --chown=appuser:appuser . /app

USER appuser

# Collect versioned static assets in the image so startup stays immutable.
RUN SECRET_KEY=static-build-only-secret-key-not-used-at-runtime \
    ALLOWED_HOSTS=localhost \
    python -m manage collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "settings.wsgi:application"]
