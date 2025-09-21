#!/bin/bash

echo "🌐 Starting Next.js Frontend Only..."
echo "===================================="

cd /Users/emmanueljanot/Desktop/Code/myfund/myfundfinder/apps/web

echo "✅ Starting Next.js server on http://localhost:3000"
echo "🤖 Chatbot will be at: http://localhost:3000/chatbot"
echo "💡 Press Ctrl+C to stop"
echo ""

# Start the Next.js development server (foreground so you can see logs)
pnpm dev