import streamlit as st
import os
import sys
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.rag_engine import ingest_knowledge_base, generate_test_plan, generate_selenium_code
from app.utils import save_generated_script
from app.test_runner import run_all_test_scripts, generate_test_summary, run_selenium_script

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
if "test_results" not in st.session_state:
    st.session_state.test_results = None
if "all_scripts_generated" not in st.session_state:
    st.session_state.all_scripts_generated = False
if "script_generation_option" not in st.session_state:
    st.session_state.script_generation_option = None
if "last_generated_option" not in st.session_state:
    st.session_state.last_generated_option = None
if "single_test_result" not in st.session_state:
    st.session_state.single_test_result = None

# Main title
st.title("🤖 Autonomous QA Agent")
st.markdown("**Test Case and Script Generation System**")

# Ensure data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Show current LLM selection prominently
has_openai_key = bool(os.getenv("OPENAI_API_KEY"))
has_google_key = bool(os.getenv("GOOGLE_API_KEY"))

# Get the selected model from session state or default
if "selected_llm" not in st.session_state:
    st.session_state.selected_llm = "auto"

# Display current LLM selection in main area
col1, col2, col3 = st.columns([2, 3, 2])
with col2:
    llm_display = {
        "auto": "🤖 Auto (Google → OpenAI → Ollama)",
        "google": "🔷 Google Gemini",
        "openai": "🔵 OpenAI",
        "ollama": "🦙 Ollama (Local)"
    }
    st.info(f"**Current LLM:** {llm_display.get(st.session_state.selected_llm, 'Auto')}")

st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ LLM Configuration")
    
    # Check which models are available
    has_openai_key = bool(os.getenv("OPENAI_API_KEY"))
    has_google_key = bool(os.getenv("GOOGLE_API_KEY"))
    
    # Model selection with radio buttons for better UX
    st.subheader("Choose LLM Provider")
    
    # Show availability status
    st.markdown("**Available Models:**")
    
    col1, col2 = st.columns(2)
    with col1:
        if has_google_key:
            st.success("✅ Google Gemini")
        else:
            st.error("❌ Google Gemini")
            st.caption("Set GOOGLE_API_KEY")
    
    with col2:
        if has_openai_key:
            st.success("✅ OpenAI")
        else:
            st.error("❌ OpenAI")
            st.caption("Set OPENAI_API_KEY")
    
    st.markdown("---")
    
    # Model selection
    model_choice = st.radio(
        "Select LLM to use:",
        options=["auto", "google", "openai", "ollama"],
        index=0,
        help="Choose which LLM provider to use for generating test cases and scripts"
    )
    
    # Show detailed info based on selection
    st.markdown("---")
    st.markdown("**Selection Details:**")
    
    if model_choice == "auto":
        st.info("🤖 **Auto Mode**\n\nWill try in this order:\n1. Google Gemini (if available)\n2. OpenAI (if available)\n3. Ollama (if running)")
        if not has_google_key and not has_openai_key:
            st.warning("⚠️ No API keys found. Auto mode will try Ollama only.")
    elif model_choice == "google":
        if has_google_key:
            st.success("✅ Google Gemini is configured and ready!")
        else:
            st.error("❌ GOOGLE_API_KEY not set in .env file")
            st.info("💡 Add `GOOGLE_API_KEY=your_key_here` to your .env file")
    elif model_choice == "openai":
        if has_openai_key:
            st.success("✅ OpenAI is configured and ready!")
        else:
            st.error("❌ OPENAI_API_KEY not set in .env file")
            st.info("💡 Add `OPENAI_API_KEY=your_key_here` to your .env file")
    elif model_choice == "ollama":
        st.info("🦙 **Ollama (Local)**\n\nRequires:\n1. Ollama installed\n2. Service running: `ollama serve`\n3. Model pulled: `ollama pull llama3.2`")
        st.warning("⚠️ Make sure Ollama is running before use")
    
    selected_model = model_choice
    st.session_state.selected_llm = model_choice
    
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
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    force_rebuild = st.checkbox(
        "Force Rebuild (Delete existing)",
        value=True,
        help="If checked, will delete and rebuild the knowledge base. Uncheck to update existing."
    )
with col2:
    build_kb_button = st.button(
        "🔨 Build Knowledge Base",
        type="primary",
        use_container_width=True,
        help="Process all uploaded documents and build the vector database"
    )

if build_kb_button:
    with st.spinner("🧠 Building knowledge base... This may take a moment."):
        try:
            result = ingest_knowledge_base(force_rebuild=force_rebuild)
            
            if result.get("success"):
                st.session_state.knowledge_base_built = True
                st.success(result["message"])
                st.info(f"📊 Processed {result.get('chunks', 0)} chunks from {result.get('documents', 0)} documents")
            else:
                st.error(result["message"])
                if "locked" in result.get("message", "").lower() or "permission" in result.get("message", "").lower():
                    st.warning("💡 **Tip:** The database file is locked. Try:")
                    st.markdown("""
                    1. Close any other instances of this application
                    2. Uncheck "Force Rebuild" and try again (will update existing database)
                    3. Restart your computer if the file is still locked
                    """)
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            import traceback
            with st.expander("Show full error details"):
                st.code(traceback.format_exc())

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
        # Show which model will be used
        model_names = {
            "auto": "Auto Mode",
            "google": "Google Gemini",
            "openai": "OpenAI",
            "ollama": "Ollama"
        }
        st.info(f"🔄 Using **{model_names.get(selected_model, 'Auto Mode')}** to generate test cases...")
        
        with st.spinner("📝 Generating test cases... This may take a moment."):
            try:
                result = generate_test_plan(query=test_query, model_type=selected_model)
                
                if result.get("success"):
                    st.session_state.test_cases = result.get("test_cases", [])
                    st.success(result["message"])
                else:
                    st.error(result["message"])
                    error_msg = result.get("message", "").lower()
                    if "ollama" in error_msg and "running" in error_msg:
                        st.info("""
                        **To use Ollama:**
                        1. Install Ollama from https://ollama.ai/
                        2. Open a terminal and run: `ollama serve`
                        3. In another terminal, pull a model: `ollama pull llama3.2`
                        4. Or select a different model (OpenAI/Google) from the sidebar
                        """)
                    elif "api_key" in error_msg or "api" in error_msg:
                        st.info("""
                        **To use cloud models:**
                        1. Create a `.env` file in the project root
                        2. Add your API key: `OPENAI_API_KEY=your_key_here` or `GOOGLE_API_KEY=your_key_here`
                        3. Restart the application
                        """)
                    if "raw_response" in result:
                        with st.expander("View Raw Response"):
                            st.text(result["raw_response"])
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                if "ollama" in str(e).lower() and "connection" in str(e).lower():
                    st.info("💡 **Tip:** Ollama is not running. Start it with 'ollama serve' or select a different model.")

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

# Phase 3: Selenium Script Generation & Test Execution
st.header("🤖 Phase 3: Selenium Script Generation & Test Execution")

if not st.session_state.test_cases:
    st.warning("⚠️ Please generate test cases first in Phase 2.")
else:
    # Create dropdown options: individual test cases + "All" option
    test_case_options = {
        f"{tc.get('id', 'Unknown')}: {tc.get('title', 'No title')}": tc
        for tc in st.session_state.test_cases
    }
    dropdown_options = ["-- Select an option --"] + list(test_case_options.keys()) + ["All Test Cases"]
    
    selected_option = st.selectbox(
        "Select test case(s) to generate Selenium script:",
        options=dropdown_options,
        index=0,
        help="Choose a single test case or 'All Test Cases' to generate scripts for all"
    )
    
    # Check if selection changed and needs processing
    needs_generation = (
        selected_option != "-- Select an option --" and
        selected_option != st.session_state.last_generated_option
    )
    
    if needs_generation:
        st.session_state.script_generation_option = selected_option
        st.session_state.last_generated_option = selected_option
        
        # Read HTML if available
        html_path = Path("data/checkout.html")
        html_content = None
        if html_path.exists():
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        
        if selected_option == "All Test Cases":
            # Generate scripts for all test cases, then run all tests, then show report
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_tcs = len(st.session_state.test_cases)
            generated_count = 0
            failed_count = 0
            
            # Step 1: Generate all scripts
            status_text.text("📝 Step 1/3: Generating scripts for all test cases...")
            for idx, test_case in enumerate(st.session_state.test_cases):
                tc_id = test_case.get("id", f"TC-{idx+1:03d}")
                progress_bar.progress((idx + 1) / (total_tcs * 3))  # Divide by 3 for 3 steps
                
                result = generate_selenium_code(
                    test_case_json=test_case,
                    html_content=html_content,
                    model_type=selected_model
                )
                
                if result.get("success"):
                    filename = f"{tc_id}.py"
                    save_generated_script(filename, result.get("code", ""))
                    generated_count += 1
                else:
                    failed_count += 1
            
            # Step 2: Run all tests
            status_text.text("▶️ Step 2/3: Running all test scripts...")
            progress_bar.progress((total_tcs + 1) / (total_tcs * 3))
            
            results = run_all_test_scripts(st.session_state.test_cases)
            
            # Step 3: Generate report
            status_text.text("📊 Step 3/3: Generating test execution report...")
            progress_bar.progress(1.0)
            
            summary = generate_test_summary(results)
            st.session_state.test_results = summary
            
            progress_bar.empty()
            status_text.empty()
            
            if generated_count > 0:
                st.success(f"✅ Generated {generated_count} scripts and executed all tests! See report below.")
            if failed_count > 0:
                st.warning(f"⚠️ Failed to generate {failed_count} script(s)")
        else:
            # Generate script for single test case
            selected_test_case = test_case_options[selected_option]
            st.session_state.selected_test_case = selected_test_case
            
            model_names = {
                "auto": "Auto Mode",
                "google": "Google Gemini",
                "openai": "OpenAI",
                "ollama": "Ollama"
            }
            st.info(f"🔄 Using **{model_names.get(selected_model, 'Auto Mode')}** to generate Selenium script...")
            
            with st.spinner("🤖 Generating Selenium script... This may take a moment."):
                result = generate_selenium_code(
                    test_case_json=selected_test_case,
                    html_content=html_content,
                    model_type=selected_model
                )
                
                if result.get("success"):
                    st.session_state.generated_script = result.get("code", "")
                    # Auto-save the script
                    tc_id = selected_test_case.get("id", "test_case")
                    filename = f"{tc_id}.py"
                    saved_path = save_generated_script(filename, st.session_state.generated_script)
                    st.success(f"✅ {result['message']} Script saved to: {saved_path}")
                    
                    # Run the script immediately to get pass/fail status
                    with st.spinner("▶️ Running test script..."):
                        execution_result = run_selenium_script(saved_path)
                        st.session_state.single_test_result = execution_result
                else:
                    st.error(result["message"])
                    st.session_state.single_test_result = None
    
    # Display test result and actions for single test case
    if st.session_state.single_test_result and selected_option != "All Test Cases" and selected_option != "-- Select an option --":
        st.markdown("### 📊 Test Execution Result")
        
        result = st.session_state.single_test_result
        tc_id = st.session_state.selected_test_case.get("id", "Unknown")
        
        # Display pass/fail status
        if result.get("passed", False):
            st.success(f"✅ **{tc_id}**: PASSED")
            if result.get("execution_time"):
                st.info(f"⏱️ Execution Time: {result.get('execution_time')}s")
        else:
            st.error(f"❌ **{tc_id}**: FAILED")
            if result.get("message"):
                st.warning(f"**Error:** {result.get('message')}")
            if result.get("execution_time"):
                st.info(f"⏱️ Execution Time: {result.get('execution_time')}s")
        
        # Show output if available
        if result.get("stdout"):
            with st.expander("📄 View Test Output"):
                st.code(result.get("stdout", ""), language="text")
        
        if result.get("stderr"):
            with st.expander("⚠️ View Error Details"):
                st.code(result.get("stderr", ""), language="text")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="⬇️ Download Script",
                data=st.session_state.generated_script,
                file_name=f"{tc_id}.py",
                mime="text/x-python",
                use_container_width=True
            )
        with col2:
            if st.button("🔄 Retry", use_container_width=True):
                st.session_state.generated_script = None
                st.session_state.single_test_result = None
                st.session_state.last_generated_option = None
                st.rerun()

# Phase 4: Test Execution Results
if st.session_state.test_results:
    st.markdown("---")
    st.header("📊 Phase 4: Test Execution Report")
    
    summary = st.session_state.test_results
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tests", summary["total"])
    with col2:
        st.metric("✅ Passed", summary["passed"], delta=f"{summary['pass_rate']}%")
    with col3:
        st.metric("❌ Failed", summary["failed"])
    with col4:
        st.metric("⚠️ Not Found", summary.get("not_found", 0))
    
    st.markdown("---")
    st.markdown("### 📋 Detailed Test Results")
    
    # Display results in a table
    results_data = []
    for result in summary["results"]:
        tc = result.get("test_case", {})
        tc_id = tc.get("id", "Unknown")
        status = result.get("status", "unknown")
        passed = result.get("passed", False)
        
        # Format status with emoji
        if passed:
            status_display = "✅ Passed"
        elif status == "failed":
            status_display = "❌ Failed"
        elif status == "not_found":
            status_display = "⚠️ Script Not Found"
        elif status == "timeout":
            status_display = "⏱️ Timeout"
        elif status == "error":
            status_display = "🔴 Error"
        else:
            status_display = f"❓ {status}"
        
        results_data.append({
            "Test Case ID": tc_id,
            "Title": tc.get("title", "N/A"),
            "Status": status_display,
            "Execution Time": f"{result.get('execution_time', 0)}s" if result.get("execution_time") else "N/A",
            "Message": result.get("message", "")[:50] + "..." if len(result.get("message", "")) > 50 else result.get("message", "N/A")
        })
    
    if results_data:
        import pandas as pd
        df = pd.DataFrame(results_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Expandable details for each test
        st.markdown("#### 📄 Detailed Results")
        for result in summary["results"]:
            tc = result.get("test_case", {})
            tc_id = tc.get("id", "Unknown")
            status = result.get("status", "unknown")
            passed = result.get("passed", False)
            
            with st.expander(f"{tc_id}: {tc.get('title', 'N/A')} - {'✅ Passed' if passed else '❌ Failed'}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.json(tc)
                with col2:
                    st.markdown("**Execution Details:**")
                    st.write(f"**Status:** {status}")
                    st.write(f"**Passed:** {passed}")
                    st.write(f"**Message:** {result.get('message', 'N/A')}")
                    if result.get("execution_time"):
                        st.write(f"**Execution Time:** {result.get('execution_time')}s")
                    if result.get("stdout"):
                        st.markdown("**Output:**")
                        st.code(result.get("stdout", ""), language="text")
                    if result.get("stderr"):
                        st.markdown("**Errors:**")
                        st.code(result.get("stderr", ""), language="text")
        
        # Final summary text
        st.markdown("---")
        st.markdown("### 📝 Final Summary")
        summary_text = "**Test Execution Summary:**\n\n"
        for result in summary["results"]:
            tc = result.get("test_case", {})
            tc_id = tc.get("id", "Unknown")
            passed = result.get("passed", False)
            status_text = "Passed" if passed else "Failed"
            summary_text += f"- **{tc_id}**: {status_text}\n"
        
        st.markdown(summary_text)
        
        # Download report
        report_text = "Test Execution Report\n" + "="*50 + "\n\n"
        report_text += f"Total Tests: {summary['total']}\n"
        report_text += f"Passed: {summary['passed']}\n"
        report_text += f"Failed: {summary['failed']}\n"
        report_text += f"Pass Rate: {summary['pass_rate']}%\n\n"
        report_text += "Detailed Results:\n" + "-"*50 + "\n"
        for result in summary["results"]:
            tc = result.get("test_case", {})
            tc_id = tc.get("id", "Unknown")
            passed = result.get("passed", False)
            status_text = "Passed" if passed else "Failed"
            report_text += f"{tc_id}: {status_text}\n"
        
        st.download_button(
            label="📥 Download Test Report",
            data=report_text,
            file_name="test_execution_report.txt",
            mime="text/plain"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Autonomous QA Agent - Test Case and Script Generation System</p>
</div>
""", unsafe_allow_html=True)

