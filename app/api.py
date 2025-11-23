import os
import sys
import json
import shutil
import time
from typing import List, Dict, Optional, Any
from pathlib import Path
from contextlib import asynccontextmanager

# FastAPI Imports
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# LangChain Imports
from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv

load_dotenv()

# --- Import Fallbacks for LLMs ---
try:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

try:
    from langchain_community.llms import Ollama

    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings

    HAS_HF_EMBEDDINGS = True
except ImportError:
    HAS_HF_EMBEDDINGS = False

# --- Utils Import (Path Setup) ---
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from app.utils import clean_llm_json, clean_python_code
except ImportError:
    # Fallback mock functions if utils are missing during testing
    def clean_llm_json(text):
        return json.loads(text) if isinstance(text, str) else text


    def clean_python_code(text):
        return text.replace("```python", "").replace("```", "").strip()

# --- Configuration ---
VECTOR_DB_PATH = "chroma_db_store"
DATA_PATH = "data"


# ==========================================
# 1. Pydantic Models (Request/Response Schemas)
# ==========================================

class IngestRequest(BaseModel):
    data_path: Optional[str] = DATA_PATH
    force_rebuild: bool = False


class TestGenRequest(BaseModel):
    query: str = "Generate comprehensive test cases"
    model_type: str = "auto"
    k_context: int = 5


class CodeGenRequest(BaseModel):
    test_case: Dict[str, Any]
    html_content: Optional[str] = None
    model_type: str = "auto"


class StatusResponse(BaseModel):
    status: str
    llms_available: Dict[str, bool]
    vector_db_exists: bool


# ==========================================
# 2. Service Logic (Refactored)
# ==========================================

def get_embeddings():
    """Get embeddings model - prefer local, fallback to OpenAI"""
    if HAS_HF_EMBEDDINGS:
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
        return OpenAIEmbeddings()
    raise HTTPException(status_code=500, detail="No embeddings model available.")


def get_llm_instance(model_type: str = "auto", temperature: float = 0.1):
    """Get LLM Instance based on type"""
    if model_type == "auto":
        if HAS_GOOGLE and os.getenv("GOOGLE_API_KEY"):
            return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=temperature)
        if HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
            return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
        if HAS_OLLAMA:
            return Ollama(model="llama3.2", temperature=temperature)
        raise HTTPException(status_code=500, detail="No LLM available. Check API keys or Ollama.")

    if model_type == "ollama":
        return Ollama(model="llama3.2", temperature=temperature)
    elif model_type == "openai":
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
    elif model_type == "google":
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=temperature)

    raise HTTPException(status_code=400, detail=f"Unknown model type: {model_type}")


# ==========================================
# 3. FastAPI App Setup
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create data dirs if they don't exist
    os.makedirs(DATA_PATH, exist_ok=True)
    print("--- 🚀 QA Agent API Started ---")
    yield
    # Shutdown logic (if any)
    print("--- 🛑 QA Agent API Stopped ---")


app = FastAPI(
    title="EcoVision QA Agent API",
    description="Autonomous QA Agent for Test Case & Selenium Script Generation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 4. Endpoints
# ==========================================

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "active", "message": "QA Agent API is running"}


@app.get("/status", response_model=StatusResponse, tags=["Health"])
async def system_status():
    return {
        "status": "online",
        "llms_available": {
            "openai": HAS_OPENAI,
            "google": HAS_GOOGLE,
            "ollama": HAS_OLLAMA,
            "hf_embeddings": HAS_HF_EMBEDDINGS
        },
        "vector_db_exists": os.path.exists(VECTOR_DB_PATH)
    }


@app.post("/ingest", tags=["Knowledge Base"])
async def ingest_data(request: IngestRequest):
    """Builds the RAG knowledge base from the data directory."""
    try:
        data_dir = request.data_path or DATA_PATH
        if not os.path.exists(data_dir):
            raise HTTPException(status_code=404, detail=f"Data directory not found: {data_dir}")

        # Logic for Loading
        loaders = [
            DirectoryLoader(data_dir, glob="**/*.md", loader_cls=TextLoader),
            DirectoryLoader(data_dir, glob="**/*.txt", loader_cls=TextLoader),
            DirectoryLoader(data_dir, glob="**/*.json", loader_cls=TextLoader),
            DirectoryLoader(data_dir, glob="**/*.html", loader_cls=UnstructuredHTMLLoader),
        ]

        documents = []
        for loader in loaders:
            try:
                documents.extend(loader.load())
            except Exception:
                pass  # Skip problematic loaders

        if not documents:
            return {"success": False, "message": "No documents found."}

        # Logic for Splitting
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)

        # Logic for Rebuilding DB
        if request.force_rebuild and os.path.exists(VECTOR_DB_PATH):
            try:
                shutil.rmtree(VECTOR_DB_PATH)
                time.sleep(1)  # brief pause to release locks
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Could not clear existing DB: {str(e)}")

        # Create Vector Store
        embeddings = get_embeddings()
        vector_db = Chroma.from_documents(chunks, embeddings, persist_directory=VECTOR_DB_PATH)
        vector_db.persist()

        return {
            "success": True,
            "message": f"Processed {len(chunks)} chunks from {len(documents)} documents.",
            "chunks_count": len(chunks)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/tests", tags=["Generation"])
async def generate_tests(request: TestGenRequest):
    """Generates test cases using RAG."""
    if not os.path.exists(VECTOR_DB_PATH):
        raise HTTPException(status_code=400, detail="Knowledge base not found. Run /ingest first.")

    try:
        embeddings = get_embeddings()
        vector_db = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
        retriever = vector_db.as_retriever(search_kwargs={"k": request.k_context})

        llm = get_llm_instance(request.model_type)

        prompt_template = """
        You are a Senior QA Architect. Based STRICTLY on the provided Context, generate a comprehensive list of Test Cases.
        CONTEXT: {context}
        QUERY: {query}
        OUTPUT FORMAT (JSON ONLY):
        [
          {{
            "id": "TC-001",
            "title": "Short descriptive title",
            "description": "Detailed description",
            "expected_result": "Expected outcome",
            "source_document": "filename.md"
          }}
        ]
        """
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "query"])

        chain = (
                {"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
                 "query": RunnablePassthrough()}
                | PROMPT
                | llm
                | StrOutputParser()
        )

        raw_response = chain.invoke(request.query)
        structured_data = clean_llm_json(raw_response)

        return {"success": True, "test_cases": structured_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/generate/code", tags=["Generation"])
async def generate_selenium(request: CodeGenRequest):
    """Generates Python Selenium code for a specific test case."""

    # Handle HTML Content
    html_content = request.html_content
    if not html_content:
        # Try to find default file
        default_html = os.path.join(DATA_PATH, "checkout.html")
        if os.path.exists(default_html):
            with open(default_html, "r", encoding="utf-8") as f:
                html_content = f.read()
        else:
            raise HTTPException(status_code=400,
                                detail="HTML content not provided and default checkout.html not found.")

    try:
        # Retrieve RAG context (optional but helpful)
        doc_context = ""
        if os.path.exists(VECTOR_DB_PATH):
            embeddings = get_embeddings()
            vector_db = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
            retriever = vector_db.as_retriever(search_kwargs={"k": 2})
            docs = retriever.get_relevant_documents(
                f"{request.test_case.get('title')} {request.test_case.get('description')}")
            doc_context = "\n".join([d.page_content for d in docs])

        llm = get_llm_instance(request.model_type)

        prompt = f"""
        You are an expert Automation Engineer (Python Selenium). Write a script for:
        TEST CASE: {json.dumps(request.test_case)}
        HTML CONTEXT: {html_content}
        DOCS CONTEXT: {doc_context}

        REQUIREMENTS:
        - Use 'webdriver.Chrome()'
        - Use Explicit Waits (WebDriverWait)
        - Output ONLY raw Python code.
        """

        response = llm.invoke(prompt)
        code = response.content if hasattr(response, 'content') else str(response)
        clean_code = clean_python_code(code)

        return {"success": True, "code": clean_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)