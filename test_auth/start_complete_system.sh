#!/bin/bash

echo "🚀 Starting Complete SME RAG Chatbot System"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if AWS is configured
print_status "Checking AWS configuration..."
if aws sts get-caller-identity >/dev/null 2>&1; then
    print_success "AWS credentials are working"
else
    print_error "AWS credentials not configured. Please run 'aws configure'"
    exit 1
fi

# Start chatbot backend
print_status "Starting chatbot backend server..."
cd /Users/emmanueljanot/Desktop/Code/test_auth

# Activate virtual environment and start server
source rag_env/bin/activate

# Kill any existing chatbot processes
pkill -f chatbot_app.py >/dev/null 2>&1

# Start the backend server in background
python3 chatbot_app.py > chatbot_backend.log 2>&1 &
BACKEND_PID=$!

print_success "Chatbot backend started (PID: $BACKEND_PID)"

# Wait for backend to start
print_status "Waiting for backend to initialize..."
sleep 5

# Check if backend is responding
if curl -s http://localhost:8081/status >/dev/null 2>&1; then
    print_success "Backend is responding on http://localhost:8081"
else
    print_error "Backend failed to start. Check chatbot_backend.log"
    exit 1
fi

# Start Next.js frontend
print_status "Starting Next.js frontend..."
cd /Users/emmanueljanot/Desktop/Code/myfund/myfundfinder

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    pnpm install
fi

# Start the Next.js development server
print_status "Starting Next.js development server..."
cd apps/web

# Start in background
pnpm dev > nextjs_frontend.log 2>&1 &
FRONTEND_PID=$!

print_success "Next.js frontend started (PID: $FRONTEND_PID)"

# Wait for frontend to start
print_status "Waiting for Next.js to initialize..."
sleep 10

echo ""
echo "🎉 System is now running!"
echo "=========================="
echo ""
echo "📱 Frontend (Next.js): http://localhost:3000"
echo "   Navigate to: http://localhost:3000/chatbot"
echo ""
echo "🤖 Backend API: http://localhost:8081"
echo "   Direct chatbot: http://localhost:8081"
echo ""
echo "📁 Your S3 bucket: sme-rag-documents-1758382778"
echo ""
echo "💡 To stop the system:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📋 Logs:"
echo "   Backend: /Users/emmanueljanot/Desktop/Code/test_auth/chatbot_backend.log"
echo "   Frontend: /Users/emmanueljanot/Desktop/Code/myfund/myfundfinder/apps/web/nextjs_frontend.log"
echo ""

# Keep script running and monitor
print_status "System is running. Press Ctrl+C to stop..."

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down system..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    print_success "System stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Wait indefinitely
wait