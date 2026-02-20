#!/bin/bash

# Start Redis in the background
echo "Starting Redis..."
redis-server --daemonize yes

# Wait for Redis
until redis-cli ping; do
  echo "Waiting for Redis..."
  sleep 1
done

# Start Celery worker in the background
echo "Starting Celery Worker..."
cd api_server
celery -A app.workers.celery_app worker --loglevel=info &

# Start the FastAPI application
echo "Starting FastAPI Server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
