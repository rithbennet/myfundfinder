#!/usr/bin/env python3
"""
Simple server startup script to avoid import issues
"""
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from app.main import app
    print("✅ FastAPI app imported successfully")
    
    if __name__ == "__main__":
        import uvicorn
        print("🚀 Starting FastAPI server...")
        uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)