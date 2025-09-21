#!/bin/bash

# Start both servers for testing the chat integration

echo "Starting FastAPI server..."
cd ai
source .venv/bin/activate
python run_dev.py &
AI_PID=$!

echo "Starting Next.js web server..."
cd ../web
npm run dev &
WEB_PID=$!

echo "Both servers started!"
echo "FastAPI: http://localhost:8000"
echo "Next.js: http://localhost:3000"
echo "Chat test page: http://localhost:3000/chat-test"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for interrupt
trap "kill $AI_PID $WEB_PID; exit" INT
wait
