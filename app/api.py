from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import json
from pathlib import Path

from app.rag_engine import ingest_knowledge_base, generate_test_plan, generate_selenium_code
from app.utils import save_generated_script

app = FastAPI(
    title="Autonomous QA Agent API",
    description="API for test case and Selenium script generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class TestCaseRequest(BaseModel):
    query: str = "Generate comprehensive test cases"
    model_type: str = "auto"
    k: int = 5

class ScriptGenerationRequest(BaseModel):
    test_case: Dict
    html_content: Optional[str] = None
    model_type: str = "auto"

class KnowledgeBaseResponse(BaseModel):
    success: bool
    message: str
    chunks: Optional[int] = None
    documents: Optional[int] = None

class TestPlanResponse(BaseModel):
    success: bool
    message: str
    test_cases: List[Dict]

class ScriptResponse(BaseModel):
    success: bool
    message: str
    code: str
    file_path: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Autonomous QA Agent API",
        "version": "1.0.0",
        "endpoints": {
            "build_kb": "/api/knowledge-base/build",
            "generate_test_cases": "/api/test-cases/generate",
            "generate_script": "/api/scripts/generate"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/knowledge-base/build", response_model=KnowledgeBaseResponse)
async def build_knowledge_base(
    force_rebuild: bool = Form(True),
    data_path: Optional[str] = Form(None)
):
    """
    Build or rebuild the knowledge base from documents in the data directory.
    
    Args:
        force_rebuild: Whether to rebuild the knowledge base if it already exists
        data_path: Optional custom path to data directory
    
    Returns:
        KnowledgeBaseResponse with success status and message
    """
    try:
        result = ingest_knowledge_base(data_path=data_path, force_rebuild=force_rebuild)
        return KnowledgeBaseResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload support documents to the data directory.
    
    Args:
        files: List of files to upload (MD, TXT, JSON, PDF, HTML)
    
    Returns:
        Success message with uploaded file names
    """
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    uploaded_files = []
    for file in files:
        try:
            file_path = data_dir / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            uploaded_files.append(file.filename)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading {file.filename}: {str(e)}"
            )
    
    return {
        "success": True,
        "message": f"Successfully uploaded {len(uploaded_files)} file(s)",
        "files": uploaded_files
    }


@app.post("/api/test-cases/generate", response_model=TestPlanResponse)
async def generate_test_cases(request: TestCaseRequest):
    """
    Generate test cases based on the knowledge base.
    
    Args:
        request: TestCaseRequest with query, model_type, and k parameters
    
    Returns:
        TestPlanResponse with generated test cases
    """
    try:
        result = generate_test_plan(
            query=request.query,
            model_type=request.model_type,
            k=request.k
        )
        return TestPlanResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scripts/generate", response_model=ScriptResponse)
async def generate_script(request: ScriptGenerationRequest):
    """
    Generate a Selenium script for a given test case.
    
    Args:
        request: ScriptGenerationRequest with test_case, html_content, and model_type
    
    Returns:
        ScriptResponse with generated Python code
    """
    try:
        # If HTML content not provided, try to read from file
        html_content = request.html_content
        if not html_content:
            html_path = Path("data/checkout.html")
            if html_path.exists():
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
        
        result = generate_selenium_code(
            test_case_json=request.test_case,
            html_content=html_content,
            model_type=request.model_type
        )
        
        # Optionally save the script
        file_path = None
        if result.get("success") and result.get("code"):
            tc_id = request.test_case.get("id", "test_case")
            filename = f"{tc_id}.py"
            file_path = save_generated_script(filename, result["code"])
            result["file_path"] = file_path
        
        return ScriptResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/test-cases/list")
async def list_test_cases():
    """
    List all test cases if they exist in session/cache.
    Note: This is a simple implementation. In production, you might want to use a database.
    """
    # This would typically come from a database or cache
    # For now, return empty list
    return {
        "success": True,
        "test_cases": []
    }


@app.get("/api/knowledge-base/status")
async def knowledge_base_status():
    """
    Check if knowledge base exists and is ready.
    """
    kb_path = Path("chroma_db_store")
    exists = kb_path.exists() and any(kb_path.iterdir())
    
    return {
        "exists": exists,
        "path": str(kb_path) if exists else None,
        "ready": exists
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

