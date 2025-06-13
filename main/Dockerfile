# Dockerfile at project root
FROM python:3.12-slim

# System deps you’ll probably need
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential netcat && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static and run migrations at container start
CMD bash -c "
  python manage.py migrate --noinput &&
  python manage.py collectstatic --noinput &&
  uvicorn project.asgi:application --host 0.0.0.0 --port $PORT
"
