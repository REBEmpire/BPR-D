#!/bin/bash
uvicorn main:app --app-dir crewai-service --port 8000 --host 0.0.0.0 > server.log 2>&1 &
PID=$!
echo "Server started with PID $PID"
sleep 5

echo "Testing Health Check..."
curl -v http://localhost:8000/api/v1/health

echo "\nTesting Agent List..."
curl -v http://localhost:8000/api/v1/agents

echo "\nTesting Meeting Execution (Short Dummy)..."
# Just to see if it accepts the request. The actual execution takes time and might timeout or cost tokens.
# I'll use a very short agenda to minimize cost if it runs.
curl -X POST http://localhost:8000/api/v1/meetings/execute   -H "Content-Type: application/json"   -d '{"meeting_type": "daily_briefing", "agenda": "Server connectivity test only. Brief response."}'

echo "\nStopping Server..."
kill $PID
cat server.log
