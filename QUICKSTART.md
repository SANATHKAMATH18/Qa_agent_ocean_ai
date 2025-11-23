# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Setup Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: (Optional) Setup LLM

**Option A: Use Ollama (Recommended - Free & Local)**
```bash
# Install Ollama from https://ollama.ai/
# Then pull a model:
ollama pull llama3.2
```

**Option B: Use Cloud APIs**
```bash
# Create .env file
cp .env.example .env
# Edit .env and add your API keys
```

### Step 3: Run the Application

**Streamlit UI (Recommended):**
```bash
streamlit run app/ui.py
# Or simply:
python main.py
```

**FastAPI Backend:**
```bash
python run_api.py
# Then visit http://localhost:8000/docs
```

## 📋 Usage Workflow

1. **Upload Documents**: Upload your support documents (MD, TXT, JSON, PDF) or use the existing ones in `data/`
2. **Upload HTML**: Upload or paste your `checkout.html` file
3. **Build KB**: Click "Build Knowledge Base" to process documents
4. **Generate Tests**: Enter a query and click "Generate Test Cases"
5. **Select Test**: Choose a test case from the list
6. **Generate Script**: Click "Generate Selenium Script"
7. **Save/Download**: Save or download the generated script

## 🎯 Example Queries

- `"Generate comprehensive test cases covering all features"`
- `"Generate test cases for discount code feature"`
- `"Generate test cases for form validation"`
- `"Generate test cases for payment processing"`

## ⚠️ Troubleshooting

**No LLM available?**
- Install Ollama: https://ollama.ai/
- Or set API keys in `.env` file

**Knowledge base not found?**
- Click "Build Knowledge Base" button first

**Import errors?**
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check API docs at `http://localhost:8000/docs` (if using FastAPI)
- Review generated scripts in `generated_scripts/` folder

