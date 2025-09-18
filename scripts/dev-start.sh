#!/bin/bash
echo "🚀 Starting TourWithEase Development Environment"
# Check if Redis is running
if ! docker ps | grep -q redis; then
echo "📦 Starting Redis..."
docker-compose up -d redis
sleep 2
fi
# Start Python ADK agents in background
echo "🐍 Starting Python ADK agents..."
cd backend/api-gateway/python-agents
source venv/bin/activate
python main.py &
PYTHON_PID=$!
cd ../../..
# Start Node.js services
echo "🚀 Starting development servers..."
# Use trap to cleanup background processes
trap 'kill $PYTHON_PID 2>/dev/null' EXIT
# Start all Node.js services concurrently
npm run dev
# Cleanup
kill $PYTHON_PID 2>/dev/null