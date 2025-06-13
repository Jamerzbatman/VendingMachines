# ─────────────────────────────────────────────────────────
# Dockerfile – drop this in the project root directory
# ─────────────────────────────────────────────────────────
# 1. Base image
FROM python:3.12-slim

# 2. Minimal sane env settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000             

# 3. OS-level packages your project is likely to need
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential netcat && \
    rm -rf /var/lib/apt/lists/*

# 4. Create an unprivileged user (good container hygiene)
RUN addgroup --system app && adduser --system --group app
USER app
WORKDIR /app

# 5. Install Python deps
COPY --chown=app:app requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 6. Copy project code
COPY --chown=app:app . .

# 7. Expose port (handy for local docker run)
EXPOSE 8000

# 8. Optionally probe health (DELETE if you don’t have a 200 / route)
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=4 \
  CMD curl -f http://localhost:${PORT:-8000}/ || exit 1

# 9. One-liner that handles migrations, static files, **and** starts Daphne
CMD bash -c "
  python manage.py migrate --noinput &&
  python manage.py collectstatic --noinput &&
  daphne -b 0.0.0.0 -p \$PORT main.asgi:application
"
