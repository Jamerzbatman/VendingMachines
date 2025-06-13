#############################################
# Dockerfile – works for Django + Channels  #
#############################################

# 1. Base image
FROM python:3.12-slim

# 2. Environment sanity
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 3. OS-level deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# 4. App code
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .

# 5. Expose a port for local docker run (DO will override with $PORT)
EXPOSE 8000

# 6. One-liner that:
#    • applies migrations
#    • collects static files
#    • starts Daphne on whatever port DO injects
# NOTE: replace `mysite` with your Django project folder name if different.
CMD bash -c "python manage.py migrate --noinput && \
             python manage.py collectstatic --noinput && \
             daphne -b 0.0.0.0 -p \$PORT main.asgi:application"


             