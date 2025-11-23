"""
Run the FastAPI backend server.
Usage: python run_api.py
"""

import uvicorn
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Add project root to Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    print("🚀 Starting FastAPI backend...")
    print("📡 API will be available at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")
    print(f"📂 Working directory: {project_root}")
    
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)

