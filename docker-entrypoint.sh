#!/bin/sh
set -e

echo "==============================================="
echo "Gym Manager - Railway Deployment Diagnostics"
echo "==============================================="
echo "Build Time: $(date)"
echo "PORT Variable: ${PORT}"
echo "Working Directory: $(pwd)"
echo "Python Version: $(python --version)"
echo "Files in directory:"
ls -la
echo "==============================================="

# Check if PORT is set
if [ -z "$PORT" ]; then
    echo "ERROR: PORT environment variable is NOT set!"
    echo "Using default port 8080"
    export PORT=8080
else
    echo "SUCCESS: PORT is set to: $PORT"
fi

echo "Starting Gunicorn on 0.0.0.0:${PORT}"
echo "==============================================="

# Start gunicorn
exec gunicorn app:app \
  --bind "0.0.0.0:${PORT}" \
  --timeout 120 \
  --workers 2 \
  --log-level debug \
  --access-logfile - \
  --error-logfile -
