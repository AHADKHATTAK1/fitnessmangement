#!/bin/sh
set -e

# Debug: Show PORT environment variable
echo "================================================"
echo "Starting Gym Manager Application"
echo "PORT environment variable: ${PORT:-NOT_SET}"
echo "================================================"

# Use PORT from environment, default to 8080 if not set
exec gunicorn app:app \
  --bind "0.0.0.0:${PORT:-8080}" \
  --timeout 120 \
  --workers 2 \
  --access-logfile - \
  --error-logfile -
