FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Cloud Run and many hosts set PORT; default 8080 for local docker run
CMD gunicorn --workers 2 --threads 4 --bind 0.0.0.0:${PORT:-8080} app:app
