import os
import json
import shutil
from typing import List, Dict, Optional
from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from dotenv import load_dotenv

# Try to import different LLM providers
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

# Load utils
from app.utils import clean_llm_json

# Load API Keys
load_dotenv()

# Configuration
VECTOR_DB_PATH = "chroma_db_store"
DATA_PATH = "data"


def get_embeddings():
    """Get embeddings model - prefer local, fallback to OpenAI"""
    if HAS_HF_EMBEDDINGS:
        try:
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception as e:
            print(f"Warning: Could not load HuggingFace embeddings: {e}")
    
    if HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
        return OpenAIEmbeddings()
    
    raise Exception("No embeddings model available. Install sentence-transformers or set OPENAI_API_KEY")


def get_llm(model_type: str = "auto", temperature: float = 0.1):
    """Get LLM - prefer local (Ollama), fallback to cloud providers"""
    if model_type == "auto":
        # Try Ollama first (local, free)
        if HAS_OLLAMA:
            try:
                return Ollama(model="llama3.2", temperature=temperature)
            except Exception as e:
                print(f"Warning: Ollama not available: {e}")
        
        # Try OpenAI
        if HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
            return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
        
        # Try Google
        if HAS_GOOGLE and os.getenv("GOOGLE_API_KEY"):
            return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=temperature)
        
        raise Exception("No LLM available. Install Ollama or set API keys (OPENAI_API_KEY or GOOGLE_API_KEY)")
    
    elif model_type == "ollama":
        if not HAS_OLLAMA:
            raise Exception("Ollama not installed. Install with: pip install langchain-community")
        return Ollama(model="llama3.2", temperature=temperature)
    
    elif model_type == "openai":
        if not HAS_OPENAI or not os.getenv("OPENAI_API_KEY"):
            raise Exception("OpenAI not configured. Set OPENAI_API_KEY environment variable")
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
    
    elif model_type == "google":
        if not HAS_GOOGLE or not os.getenv("GOOGLE_API_KEY"):
            raise Exception("Google not configured. Set GOOGLE_API_KEY environment variable")
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=temperature)
    
    raise Exception(f"Unknown model type: {model_type}")


def ingest_knowledge_base(data_path: Optional[str] = None, force_rebuild: bool = False):
    """
    1. Reads all files from data_path (default: DATA_PATH)
    2. Splits them into chunks
    3. Saves them to ChromaDB
    """
    print("--- 🧠 Building Knowledge Base ---")
    
    data_dir = data_path or DATA_PATH
    
    if not os.path.exists(data_dir):
        return {"success": False, "message": f"❌ Data directory not found: {data_dir}"}
    
    # Define how to load each file type
    loaders = [
        DirectoryLoader(data_dir, glob="**/*.md", loader_cls=TextLoader),
        DirectoryLoader(data_dir, glob="**/*.txt", loader_cls=TextLoader),
        DirectoryLoader(data_dir, glob="**/*.json", loader_cls=TextLoader),
        DirectoryLoader(data_dir, glob="**/*.html", loader_cls=UnstructuredHTMLLoader),
    ]

    documents = []
    for loader in loaders:
        try:
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            print(f"Warning: Error loading files with {loader}: {e}")

    if not documents:
        return {"success": False, "message": f"❌ No documents found in {data_dir} folder."}

    # Chunk the text (Critical for RAG)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    # Force a fresh DB if requested
    if force_rebuild and os.path.exists(VECTOR_DB_PATH):
        shutil.rmtree(VECTOR_DB_PATH)

    try:
        # Create Vector Store
        embeddings = get_embeddings()
        vector_db = Chroma.from_documents(
            documents=chunks, 
            embedding=embeddings, 
            persist_directory=VECTOR_DB_PATH
        )
        
        return {
            "success": True,
            "message": f"✅ Knowledge Base Ready! Processed {len(chunks)} text chunks from {len(documents)} documents.",
            "chunks": len(chunks),
            "documents": len(documents)
        }
    except Exception as e:
        return {"success": False, "message": f"❌ Error building knowledge base: {str(e)}"}


def generate_test_plan(query: str = "Generate comprehensive test cases", model_type: str = "auto", k: int = 5):
    """
    Uses RAG to generate structured Test Cases based on the knowledge base.
    """
    print("--- 📝 Generating Test Plan ---")
    
    if not os.path.exists(VECTOR_DB_PATH):
        return {"success": False, "message": "❌ Knowledge base not found. Please build it first.", "test_cases": []}
    
    try:
        embeddings = get_embeddings()
        vector_db = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
        
        # Retrieve relevant context
        retriever = vector_db.as_retriever(search_kwargs={"k": k})
        
        prompt_template = """
You are a Senior QA Architect. Based STRICTLY on the provided Context, generate a comprehensive list of Test Cases.

CONTEXT:
{context}

REQUIREMENTS:
1. Cover positive flow (Happy Path) scenarios.
2. Cover negative flow (Edge Cases and error scenarios).
3. Specifically check for form validations, payment processing, discount codes, and shipping methods mentioned in the documents.
4. Each test case must reference the source document it's based on.
5. DO NOT invent features that are not mentioned in the context.

OUTPUT FORMAT (JSON ONLY, no markdown, no code blocks):
[
  {{
    "id": "TC-001",
    "title": "Short descriptive title",
    "description": "Detailed description of what to test",
    "expected_result": "What should happen when this test passes",
    "source_document": "filename.md or checkout.html"
  }}
]

Generate at least 8-12 test cases covering all features mentioned in the context.
"""
        
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context"])
        
        llm = get_llm(model_type=model_type, temperature=0.1)
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        result = qa_chain.invoke({"query": query})
        raw_response = result.get("result", "")
        
        # Use our utility to clean the JSON
        structured_data = clean_llm_json(raw_response)
        
        if isinstance(structured_data, list) and len(structured_data) > 0:
            return {
                "success": True,
                "message": f"✅ Generated {len(structured_data)} test cases.",
                "test_cases": structured_data
            }
        else:
            return {
                "success": False,
                "message": "❌ Failed to generate valid test cases. Please try again.",
                "test_cases": [],
                "raw_response": raw_response
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error generating test plan: {str(e)}",
            "test_cases": []
        }


def generate_selenium_code(test_case_json: Dict, html_content: Optional[str] = None, model_type: str = "auto"):
    """
    Generates a Python Selenium script for the given test case.
    Context: The specific Test Case + The RAW HTML file.
    """
    print(f"--- 🤖 Generating Code for {test_case_json.get('id', 'Unknown')} ---")
    
    # Read the Raw HTML if not provided
    if html_content is None:
        html_path = os.path.join(DATA_PATH, "checkout.html")
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        else:
            return {
                "success": False,
                "message": f"❌ HTML file not found at {html_path}",
                "code": ""
            }
    
    # Retrieve relevant documentation for context
    doc_context = ""
    try:
        if os.path.exists(VECTOR_DB_PATH):
            embeddings = get_embeddings()
            vector_db = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
            retriever = vector_db.as_retriever(search_kwargs={"k": 3})
            
            # Search for relevant docs based on test case
            source_doc = test_case_json.get("source_document", "")
            query = f"{test_case_json.get('title', '')} {test_case_json.get('description', '')}"
            relevant_docs = retriever.get_relevant_documents(query)
            doc_context = "\n\n".join([doc.page_content for doc in relevant_docs])
    except Exception as e:
        print(f"Warning: Could not retrieve document context: {e}")
    
    # Construct Prompt
    prompt = f"""
You are an expert Automation Engineer specializing in Python Selenium. Write a complete, runnable Python Selenium script for the following test case.

TEST CASE:
{json.dumps(test_case_json, indent=2)}

TARGET HTML FILE CONTENT:
{html_content}

RELEVANT DOCUMENTATION:
{doc_context}

REQUIREMENTS:
1. Use 'from selenium import webdriver' and 'from selenium.webdriver.common.by import By'
2. Use 'from selenium.webdriver.support.ui import WebDriverWait' and 'from selenium.webdriver.support import expected_conditions as EC'
3. Use Explicit Waits (WebDriverWait) for finding elements. DO NOT use time.sleep().
4. Use the EXACT IDs, names, or CSS selectors found in the HTML above (e.g., By.ID("discountCode"), By.NAME("shipping"), etc.).
5. Use webdriver.Chrome() with ChromeDriverManager for automatic driver management.
6. Include proper error handling and assertions.
7. Add comments explaining key steps.
8. The script should be fully executable and test the exact scenario described in the test case.
9. If the test case involves form validation, check for error messages using the exact error element IDs (e.g., "emailError").
10. If the test case involves payment, verify the success message appears.

OUTPUT ONLY the Python code, no markdown, no explanations, just the code:
"""
    
    try:
        llm = get_llm(model_type=model_type, temperature=0.0)
        response = llm.invoke(prompt)
        
        # Extract content (handle different response types)
        if hasattr(response, 'content'):
            code = response.content
        elif isinstance(response, str):
            code = response
        else:
            code = str(response)
        
        # Clean the code
        from app.utils import clean_python_code
        clean_code = clean_python_code(code)
        
        return {
            "success": True,
            "message": f"✅ Generated Selenium script for {test_case_json.get('id', 'Unknown')}",
            "code": clean_code
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error generating script: {str(e)}",
            "code": ""
        }
