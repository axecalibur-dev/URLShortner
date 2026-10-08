#!/usr/bin/env bash
set -e

# Navigate to the script's directory so it works from anywhere
cd "$(dirname "$0")"

echo "Building and starting containers in detached mode..."
docker compose up -d --build

echo "Containers started successfully."
echo "Health endpoint: http://localhost:8000/health"
echo "API Docs: http://localhost:8000/docs"
echo "Now printing logs of the server"
docker logs url-shortener-api -f