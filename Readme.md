# Autonomous QA Agent for Test Case and Script Generation

![Main UI](Ocean.png)

The **Autonomous QA Agent** is an AI-powered system that automates the QA process by reading project documentation and a target `checkout.html` file, building a knowledge base, generating accurate test cases, and converting selected test cases into runnable Python Selenium scripts.

This project demonstrates how AI can enhance software testing by reducing manual effort, improving accuracy, and ensuring test coverage aligned with project requirements.

---

## 📌 Overview

Traditional QA requires manually reading documentation, writing test cases, and then writing automation scripts. This project automates all three steps:

1.  **Ingest documents + HTML** - Upload support documents and target HTML file
2.  **Understand them using embeddings & vector search** - Build a searchable knowledge base
3.  **Generate grounded test cases** - Create test cases strictly based on provided documents
4.  **Produce Selenium scripts automatically** - Convert test cases to executable Python scripts

The result is a powerful, end-to-end QA automation assistant.

---

## 🚀 Features

* **Multi-Format Ingestion:** Upload project documents (MD, TXT, JSON, PDF, HTML).
* **HTML Parsing:** Upload or paste the target `checkout.html` file.
* **Vector Knowledge Base:** Build a searchable knowledge base using embeddings (local or cloud).
* **RAG-based Generation:** Retrieval-Augmented Generation for test case creation.
* **Strict Grounding:** No hallucinated features; relies strictly on provided documents.
* **Auto-Scripting:** Generate runnable Python Selenium scripts instantly.
* **User Interface:** Simple and intuitive Streamlit UI.
* **REST API:** FastAPI backend for programmatic access.
* **Multiple LLM Support:** Works with Ollama (local), OpenAI, or Google Gemini.

---

## 🧠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **UI** | Streamlit |
| **Backend** | FastAPI |
| **Vector DB** | ChromaDB |
| **Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`) or OpenAI |
| **Parsers** | BeautifulSoup4, PyMuPDF, Unstructured |
| **LLM Provider** | Ollama (local) / OpenAI / Google Gemini |
| **Automation** | Selenium (Python) |

---

## 📂 Project Structure

```
qa-agent-ocean-ai/
├── app/
│   ├── __init__.py
│   ├── api.py              # FastAPI backend
│   ├── ui.py               # Streamlit UI
│   ├── rag_engine.py       # RAG pipeline & LLM integration
│   └── utils.py            # Utility functions
├── data/
│   ├── checkout.html       # Target HTML file
│   ├── product_specs.md    # Product specifications
│   ├── ui_ux_guide.txt     # UI/UX guidelines
│   └── api_endpoints.json  # API documentation
├── generated_scripts/      # Generated Selenium scripts
├── chroma_db_store/        # Vector database (created automatically)
├── requirements.txt
├── test_logic.py           # Example test script
└── README.md
```

---

## 🛠️ Setup

### Prerequisites

- **Python 3.10+** (recommended: Python 3.11 or 3.12)
- **pip** (Python package manager)
- **Git** (optional, for cloning)

### Installation Steps

#### 1. Create Virtual Environment

**For Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**For Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** The installation may take a few minutes, especially when installing PyTorch and sentence-transformers.

#### 3. (Optional) Install Ollama for Local LLM

If you want to use local models without API keys:

1. Download and install [Ollama](https://ollama.ai/)
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```

#### 4. (Optional) Configure API Keys

If you prefer cloud LLMs, create a `.env` file in the project root:

```env
# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# For Google Gemini
GOOGLE_API_KEY=your_google_api_key_here
```

**Note:** The system will automatically try Ollama first (if available), then fall back to cloud providers if API keys are set.

---

## 🚀 How to Run

### Option 1: Streamlit UI (Recommended)

The Streamlit UI provides a complete graphical interface for all operations.

```bash
streamlit run app/ui.py
```

The UI will open in your browser at `http://localhost:8501`

**Usage Flow:**
1. Upload support documents (MD, TXT, JSON, PDF) or use existing files in `data/`
2. Upload or paste the `checkout.html` file
3. Click **"Build Knowledge Base"** to process documents
4. Enter a query and click **"Generate Test Cases"**
5. Select a test case from the list
6. Click **"Generate Selenium Script"** to create the automation script
7. Save or download the generated script

### Option 2: FastAPI Backend

Start the FastAPI server:

```bash
uvicorn app.api:app --reload
```

The API will be available at `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Example API Calls:**

```bash
# Build knowledge base
curl -X POST "http://localhost:8000/api/knowledge-base/build" \
  -F "force_rebuild=true"

# Generate test cases
curl -X POST "http://localhost:8000/api/test-cases/generate" \
  -H "Content-Type: application/json" \
  -d '{"query": "Generate comprehensive test cases", "model_type": "auto"}'

# Generate Selenium script
curl -X POST "http://localhost:8000/api/scripts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "test_case": {
      "id": "TC-001",
      "title": "Test discount code",
      "description": "Apply valid discount code SAVE15",
      "expected_result": "15% discount applied",
      "source_document": "product_specs.md"
    },
    "model_type": "auto"
  }'
```

### Option 3: Python Script

You can also use the RAG engine directly in Python:

```python
from app.rag_engine import ingest_knowledge_base, generate_test_plan, generate_selenium_code
from app.utils import save_generated_script

# 1. Build knowledge base
result = ingest_knowledge_base()
print(result)

# 2. Generate test cases
test_result = generate_test_plan(query="Generate comprehensive test cases")
test_cases = test_result.get("test_cases", [])

# 3. Generate script for first test case
if test_cases:
    script_result = generate_selenium_code(test_cases[0])
    if script_result.get("success"):
        print(script_result["code"])
```

---

## 📚 Included Support Documents

The `data/` directory contains example support documents:

### 1. `product_specs.md`
Contains product specifications including:
- Discount code rules (SAVE15 applies 15% discount)
- Shipping costs (Express: $10, Standard: Free)
- Payment validation requirements

### 2. `ui_ux_guide.txt`
Contains UI/UX guidelines:
- Form validation error display rules
- Button styling requirements
- Success message visibility

### 3. `api_endpoints.json`
Contains API endpoint documentation:
- POST /apply_coupon endpoint
- POST /submit_order endpoint

### 4. `checkout.html`
The target HTML file containing:
- Product items with "Add to Cart" buttons
- Cart summary with total price
- Discount code input field
- User details form (Name, Email, Address)
- Form validation with error messages
- Shipping method radio buttons
- Payment method radio buttons
- "Pay Now" button with success message

---

## 💡 Usage Examples

### Example 1: Generate Test Cases for Discount Feature

1. Build knowledge base
2. In test case query, enter: `"Generate test cases for discount code feature including valid and invalid codes"`
3. Review generated test cases
4. Select a test case (e.g., "TC-001: Apply valid discount code")
5. Generate Selenium script
6. The script will include:
   - Finding the discount code input field
   - Entering "SAVE15"
   - Clicking Apply button
   - Verifying the discount is applied

### Example 2: Test Form Validation

1. Query: `"Generate test cases for form validation including email validation and required fields"`
2. Generated test cases will cover:
   - Valid email submission
   - Invalid email format
   - Missing required fields
3. Generated scripts will check for error messages using exact element IDs

---

## 🔧 Configuration

### Model Selection

The system supports multiple LLM providers:

- **auto** (default): Tries Ollama first, then OpenAI, then Google
- **ollama**: Uses local Ollama (requires Ollama installed)
- **openai**: Uses OpenAI API (requires OPENAI_API_KEY)
- **google**: Uses Google Gemini (requires GOOGLE_API_KEY)

### Embeddings

- **Default**: Uses local `sentence-transformers/all-MiniLM-L6-v2` (no API key needed)
- **Fallback**: Uses OpenAI embeddings if API key is set

---

## 🧪 Testing Generated Scripts

Generated Selenium scripts can be run directly:

```bash
python generated_scripts/TC-001.py
```

**Prerequisites:**
- Chrome browser installed
- ChromeDriver (automatically managed by webdriver-manager)

---

## 📝 Notes

1. **Knowledge Base**: The vector database is stored in `chroma_db_store/`. Delete this folder to rebuild from scratch.

2. **Generated Scripts**: All generated scripts are saved in `generated_scripts/` directory.

3. **Document Grounding**: All test cases are strictly based on provided documents. The system will not invent features not mentioned in the documentation.

4. **HTML Selectors**: Generated scripts use exact IDs, names, and CSS selectors from the provided HTML file.

---

## 🐛 Troubleshooting

### Issue: "No LLM available"

**Solution**: Install Ollama or set API keys in `.env` file.

### Issue: "Knowledge base not found"

**Solution**: Click "Build Knowledge Base" button in the UI or call the API endpoint.

### Issue: "ChromaDB errors"

**Solution**: Delete `chroma_db_store/` folder and rebuild the knowledge base.

### Issue: "Import errors"

**Solution**: Ensure virtual environment is activated and all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "Ollama connection error"

**Solution**: Ensure Ollama is running:
```bash
ollama serve
```

---

## 📄 License

This project is created for educational and demonstration purposes.

---

## 🤝 Contributing

This is an assignment project. For questions or improvements, please refer to the assignment guidelines.

---

## 📧 Support

For issues or questions, please check:
1. The troubleshooting section above
2. API documentation at `/docs` endpoint
3. Generated script comments for debugging

---

**Happy Testing! 🚀**
