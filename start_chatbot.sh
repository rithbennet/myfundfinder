#!/bin/bash

echo "🚀 Starting SME RAG Chatbot Server..."
echo "======================================"

# Activate virtual environment
source rag_env/bin/activate

# Check if AWS credentials are working
echo "🔧 Checking AWS connection..."
if aws sts get-caller-identity >/dev/null 2>&1; then
    echo "✅ AWS credentials are working"
else
    echo "❌ AWS credentials issue - but proceeding anyway"
fi

# Check if S3 bucket is accessible
echo "🪣 Checking S3 bucket..."
if aws s3 ls s3://sme-rag-documents-1758382778/ >/dev/null 2>&1; then
    echo "✅ S3 bucket is accessible"
else
    echo "❌ S3 bucket access issue"
fi

echo ""
echo "🌐 Starting web server on http://localhost:8080"
echo "📱 The chatbot interface will open automatically"
echo "💡 To stop the server, press Ctrl+C"
echo ""
echo "🔄 Starting in 3 seconds..."
sleep 3

# Start the Flask app
python3 chatbot_app.py