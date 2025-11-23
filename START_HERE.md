# 🚀 Quick Start Guide - FastAPI + Streamlit Architecture

## ⚠️ Important: New Architecture

The Streamlit UI now **requires** the FastAPI backend to be running. The UI makes HTTP requests to the API instead of calling functions directly.

## 📋 Setup Steps

### Step 1: Activate Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 2: Start FastAPI Backend (REQUIRED)

**Open Terminal 1:**
```powershell
python run_api.py
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Step 3: Start Streamlit UI

**Open Terminal 2 (new terminal):**
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app/ui.py
```

Or use the launcher:
```powershell
python main.py
```

## ✅ Verification

1. **FastAPI should be running** at `http://localhost:8000`
2. **Streamlit UI** should show: `✅ Connected to FastAPI server at http://localhost:8000`
3. If you see an error about API connection, make sure FastAPI is running first!

## 🔄 Architecture Flow

```
┌─────────────────┐
│  Streamlit UI   │  (Terminal 2)
│   (app/ui.py)   │
└────────┬────────┘
         │ HTTP Requests
         │ (REST API)
         ▼
┌─────────────────┐
│  FastAPI Server │  (Terminal 1)
│   (app/api.py)  │
└────────┬────────┘
         │ Function Calls
         ▼
┌─────────────────┐
│   RAG Engine    │
│(app/rag_engine) │
└─────────────────┘
```

## 🛠️ Troubleshooting

**Error: "Cannot connect to FastAPI server"**
- Make sure FastAPI is running in Terminal 1
- Check that it's running on port 8000
- Verify the API URL in the UI (default: http://localhost:8000)

**Error: "Connection refused"**
- Start FastAPI first: `python run_api.py`
- Wait for the server to fully start
- Then start Streamlit

## 📝 Notes

- **Both services must run simultaneously**
- FastAPI handles all the processing logic
- Streamlit UI is now a client that calls the API
- This allows for better separation of concerns and scalability

