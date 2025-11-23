import streamlit as st
import os
import json
from pathlib import Path
from app.rag_engine import ingest_knowledge_base, generate_test_plan, generate_selenium_code
from app.utils import save_generated_script

# Page configuration
st.set_page_config(
    page_title="Autonomous QA Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "knowledge_base_built" not in st.session_state:
    st.session_state.knowledge_base_built = False
if "test_cases" not in st.session_state:
    st.session_state.test_cases = []
if "selected_test_case" not in st.session_state:
    st.session_state.selected_test_case = None
if "generated_script" not in st.session_state:
    st.session_state.generated_script = None

# Main title
st.title("🤖 Autonomous QA Agent")
st.markdown("**Test Case and Script Generation System**")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model selection
    model_options = ["auto", "ollama", "openai", "google"]
    selected_model = st.selectbox(
        "LLM Model",
        options=model_options,
        index=0,
        help="Select the LLM to use. 'auto' will try Ollama first, then cloud providers."
    )
    
    st.markdown("---")
    st.markdown("### 📚 About")
    st.markdown("""
    This system:
    1. Ingests project documentation
    2. Builds a knowledge base
    3. Generates test cases
    4. Creates Selenium scripts
    """)

# Phase 1: Document Upload and Knowledge Base Building
st.header("📥 Phase 1: Document Upload & Knowledge Base")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Support Documents")
    uploaded_docs = st.file_uploader(
        "Upload documentation files (MD, TXT, JSON, PDF)",
        type=["md", "txt", "json", "pdf"],
        accept_multiple_files=True,
        help="Upload product specs, UI/UX guides, API docs, etc."
    )
    
    if uploaded_docs:
        st.success(f"✅ {len(uploaded_docs)} file(s) uploaded")
        for doc in uploaded_docs:
            st.text(f"  • {doc.name}")

with col2:
    st.subheader("Upload or Paste HTML")
    html_option = st.radio(
        "HTML Input Method",
        ["Upload File", "Paste Content"],
        horizontal=True
    )
    
    html_content = None
    if html_option == "Upload File":
        uploaded_html = st.file_uploader(
            "Upload checkout.html",
            type=["html"],
            help="Upload the target HTML file to test"
        )
        if uploaded_html:
            html_content = uploaded_html.read().decode("utf-8")
            st.success(f"✅ {uploaded_html.name} uploaded")
    else:
        html_content = st.text_area(
            "Paste HTML content",
            height=200,
            help="Paste the HTML content directly"
        )
        if html_content:
            st.success("✅ HTML content provided")

# Save uploaded files to data directory
if uploaded_docs or html_content:
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    if uploaded_docs:
        for doc in uploaded_docs:
            file_path = data_dir / doc.name
            with open(file_path, "wb") as f:
                f.write(doc.getbuffer())
    
    if html_content and html_option == "Paste Content":
        html_path = data_dir / "checkout.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        st.info("💡 HTML saved to data/checkout.html")

# Build Knowledge Base Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    build_kb_button = st.button(
        "🔨 Build Knowledge Base",
        type="primary",
        use_container_width=True,
        help="Process all uploaded documents and build the vector database"
    )

if build_kb_button:
    with st.spinner("🧠 Building knowledge base... This may take a moment."):
        result = ingest_knowledge_base(force_rebuild=True)
        
        if result.get("success"):
            st.session_state.knowledge_base_built = True
            st.success(result["message"])
            st.info(f"📊 Processed {result.get('chunks', 0)} chunks from {result.get('documents', 0)} documents")
        else:
            st.error(result["message"])

if st.session_state.knowledge_base_built:
    st.success("✅ Knowledge Base is ready!")

st.markdown("---")

# Phase 2: Test Case Generation
st.header("📝 Phase 2: Test Case Generation")

if not st.session_state.knowledge_base_built:
    st.warning("⚠️ Please build the knowledge base first before generating test cases.")
else:
    test_query = st.text_area(
        "Test Case Query",
        value="Generate comprehensive test cases covering all features including positive and negative scenarios.",
        height=100,
        help="Describe what test cases you want to generate"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_tc_button = st.button(
            "🎯 Generate Test Cases",
            type="primary",
            use_container_width=True
        )
    
    if generate_tc_button:
        with st.spinner("📝 Generating test cases... This may take a moment."):
            result = generate_test_plan(query=test_query, model_type=selected_model)
            
            if result.get("success"):
                st.session_state.test_cases = result.get("test_cases", [])
                st.success(result["message"])
            else:
                st.error(result["message"])
                if "raw_response" in result:
                    with st.expander("View Raw Response"):
                        st.text(result["raw_response"])

# Display generated test cases
if st.session_state.test_cases:
    st.markdown("### 📋 Generated Test Cases")
    
    # Test case selector
    test_case_options = {
        f"{tc.get('id', 'Unknown')}: {tc.get('title', 'No title')}": tc
        for tc in st.session_state.test_cases
    }
    
    selected_tc_key = st.selectbox(
        "Select a test case to generate script for:",
        options=list(test_case_options.keys()),
        help="Choose a test case to convert to a Selenium script"
    )
    
    st.session_state.selected_test_case = test_case_options[selected_tc_key]
    
    # Display selected test case details
    if st.session_state.selected_test_case:
        with st.expander("📄 View Selected Test Case Details", expanded=True):
            tc = st.session_state.selected_test_case
            st.json(tc)
    
    # Display all test cases in a table
    st.markdown("#### All Test Cases")
    test_cases_df = []
    for tc in st.session_state.test_cases:
        test_cases_df.append({
            "ID": tc.get("id", "N/A"),
            "Title": tc.get("title", "N/A"),
            "Description": tc.get("description", "N/A")[:100] + "..." if len(tc.get("description", "")) > 100 else tc.get("description", "N/A"),
            "Source": tc.get("source_document", "N/A")
        })
    
    if test_cases_df:
        import pandas as pd
        st.dataframe(pd.DataFrame(test_cases_df), use_container_width=True)

st.markdown("---")

# Phase 3: Selenium Script Generation
st.header("🤖 Phase 3: Selenium Script Generation")

if not st.session_state.selected_test_case:
    st.warning("⚠️ Please select a test case first.")
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_script_button = st.button(
            "⚙️ Generate Selenium Script",
            type="primary",
            use_container_width=True
        )
    
    if generate_script_button:
        with st.spinner("🤖 Generating Selenium script... This may take a moment."):
            # Read HTML if available
            html_path = Path("data/checkout.html")
            html_content = None
            if html_path.exists():
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
            
            result = generate_selenium_code(
                test_case_json=st.session_state.selected_test_case,
                html_content=html_content,
                model_type=selected_model
            )
            
            if result.get("success"):
                st.session_state.generated_script = result.get("code", "")
                st.success(result["message"])
            else:
                st.error(result["message"])

# Display generated script
if st.session_state.generated_script:
    st.markdown("### 📜 Generated Selenium Script")
    
    # Code display
    st.code(st.session_state.generated_script, language="python")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("💾 Save Script", use_container_width=True):
            tc_id = st.session_state.selected_test_case.get("id", "test_case")
            filename = f"{tc_id}.py"
            saved_path = save_generated_script(filename, st.session_state.generated_script)
            st.success(f"✅ Script saved to: {saved_path}")
    
    with col2:
        st.download_button(
            label="⬇️ Download Script",
            data=st.session_state.generated_script,
            file_name=f"{st.session_state.selected_test_case.get('id', 'test_case')}.py",
            mime="text/x-python",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 Generate Another", use_container_width=True):
            st.session_state.generated_script = None
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Autonomous QA Agent - Test Case and Script Generation System</p>
</div>
""", unsafe_allow_html=True)

