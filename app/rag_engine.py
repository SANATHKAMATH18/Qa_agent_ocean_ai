import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load utils we just created
from app.utils import clean_llm_json

# Load API Keys
load_dotenv()

# Configuration
VECTOR_DB_PATH = "chroma_db_store"
DATA_PATH = "data"

def ingest_knowledge_base():
    """
    1. Reads all files from /data
    2. Splits them into chunks
    3. Saves them to ChromaDB
    """
    print("--- 🧠 Building Knowledge Base ---")
    
    # Define how to load each file type
    loaders = [
        DirectoryLoader(DATA_PATH, glob="**/*.md", loader_cls=TextLoader),
        DirectoryLoader(DATA_PATH, glob="**/*.txt", loader_cls=TextLoader),
        DirectoryLoader(DATA_PATH, glob="**/*.json", loader_cls=TextLoader),
        # For RAG context, we want HTML text content
        DirectoryLoader(DATA_PATH, glob="**/*.html", loader_cls=UnstructuredHTMLLoader),
    ]

    documents = []
    for loader in loaders:
        try:
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading files: {e}")

    if not documents:
        return "❌ No documents found in /data folder."

    # Chunk the text (Critical for RAG)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    # Force a fresh DB (optional: remove this if you want persistence)
    if os.path.exists(VECTOR_DB_PATH):
        shutil.rmtree(VECTOR_DB_PATH)

    # Create Vector Store
    embeddings = OpenAIEmbeddings()
    vector_db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=VECTOR_DB_PATH
    )
    
    return f"✅ Knowledge Base Ready! Processed {len(chunks)} text chunks."

def generate_test_plan():
    """
    Uses OpenAI GPT-4o to generate structured Test Cases.
    """
    print("--- 📝 Generating Test Plan ---")
    
    embeddings = OpenAIEmbeddings()
    vector_db = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
    
    # Retrieve relevant context
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    
    prompt_template = """
    You are a Senior QA Architect.
    Based strictly on the provided Context, generate a list of Test Cases.
    
    CONTEXT:
    {context}
    
    REQUIREMENTS:
    1. Cover positive flow (Happy Path).
    2. Cover negative flow (Edge Cases).
    3. specifically check for 'Payment' field validations mentioned in docs.
    
    OUTPUT FORMAT (JSON ONLY):
    [
      {{
        "id": "TC-001",
        "title": "Title of test",
        "description": "What to do",
        "expected_result": "What should happen",
        "source_document": "filename.md"
      }}
    ]
    """
    
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context"])
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    raw_response = qa_chain.run("Generate comprehensive test cases.")
    
    # Use our utility to clean the JSON
    structured_data = clean_llm_json(raw_response)
    return structured_data

def generate_selenium_code(test_case_json):
    """
    Uses Gemini 1.5 Flash to write the Selenium Script.
    Context: The specific Test Case + The RAW HTML file.
    """
    print(f"--- 🤖 Generating Code for {test_case_json.get('id')} ---")
    
    # 1. Read the Raw HTML (We need the actual ID attributes)
    html_path = os.path.join(DATA_PATH, "checkout.html")
    with open(html_path, "r", encoding="utf-8") as f:
        raw_html = f.read()

    # 2. Construct Prompt for Gemini
    prompt = f"""
    You are an Automation Engineer. Write a Python Selenium script for this test case.
    
    TEST CASE:
    {json.dumps(test_case_json, indent=2)}
    
    TARGET HTML FILE CONTENT:
    {raw_html}
    
    RULES:
    1. Use 'webdriver.Chrome()'.
    2. Use Explicit Waits (WebDriverWait) for finding elements. NO time.sleep().
    3. Use the EXACT IDs found in the HTML above (e.g. id="discountCode").
    4. Provide ONLY the Python code.
    """
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)
    response = llm.invoke(prompt)
    
    return response.content