# ───────────────────────────────
# Dockerfile (place in repo root)
# ───────────────────────────────
FROM python:3.12-slim

# ---- Runtime environment tweaks ---------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000         

# ---- OS-level deps -----------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential netcat && \
    rm -rf /var/lib/apt/lists/*

# ---- Create non-root user (good hygiene) -------------------------------------
RUN addgroup --system app && adduser --system --group app
WORKDIR /app
USER app

# ---- Python deps -------------------------------------------------------------
COPY --chown=app:app requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- Project code ------------------------------------------------------------
COPY --chown=app:app . .

# ---- Expose port for local testing ------------------------------------------
EXPOSE 8000

# ---- Health check (optional but nice) ----------------------------------------
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=4 \
  CMD curl -f http://localhost:${PORT:-8000}/ || exit 1

# ---- What actually runs ------------------------------------------------------
CMD bash -c "
  python manage.py migrate --noinput &&
  python manage.py collectstatic --noinput &&
  # Replace the dotted-path below with your real ASGI app
  daphne -b 0.0.0.0 -p \$PORT main.asgi:application
"
