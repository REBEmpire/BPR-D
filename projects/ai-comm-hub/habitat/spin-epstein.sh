#!/bin/bash
echo "Spinning up Epstein Analysis Service..."
docker compose up --build -d epstein-analysis proxy
echo "---------------------------------------------------"
echo "Epstein Analysis service live -> http://localhost:8080/agents/analysis/epstein"
echo "Healthcheck -> http://localhost:8080/health"
echo "---------------------------------------------------"
