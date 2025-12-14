#!/bin/bash
set -e

# Get port from environment variable, default to 8000
PORT=${PORT:-8000}

echo "Starting News Aggregator API on port $PORT"

# Start uvicorn
exec uvicorn news_api:app --host 0.0.0.0 --port "$PORT"

