"""
Run the FastAPI backend server.
Usage: python run_api.py
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting FastAPI backend...")
    print("📡 API will be available at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)

