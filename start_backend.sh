#!/bin/bash

echo "🤖 Starting Chatbot Backend Only..."
echo "==================================="

cd /Users/emmanueljanot/Desktop/Code/test_auth

# Activate virtual environment
source rag_env/bin/activate

# Kill any existing processes
pkill -f chatbot_app.py >/dev/null 2>&1

echo "✅ Starting backend server on http://localhost:9000"
echo "💡 Press Ctrl+C to stop"
echo ""

# Start the server (foreground so you can see logs)
python3 chatbot_app.py