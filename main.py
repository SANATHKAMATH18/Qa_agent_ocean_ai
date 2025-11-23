import streamlit as st
import os
import sys
import json
import subprocess
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
API_BASE_URL = "http://localhost:8000"  # Address of your FastAPI backend

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AutoQA Agent (Client)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE INITIALIZATION ---
if "test_cases" not in st.session_state:
    st.session_state.test_cases = []
if "generated_script" not in st.session_state:
    st.session_state.generated_script = ""
if "kb_built" not in st.session_state:
    st.session_state.kb_built = False
if "api_status" not in st.session_state:
    st.session_state.api_status = False

# --- CSS STYLING ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 5px; }
    .status-box { padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem; text-align: center; }
    .online { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .offline { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
</style>
""", unsafe_allow_html=True)


# --- HELPER: CHECK API STATUS ---
def check_api():
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=2)
        if response.status_code == 200:
            return True, response.json()
    except requests.exceptions.ConnectionError:
        pass
    return False, {}


# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/robot.png", width=100)
    st.title("⚙️ Configuration")

    # API Health Check
    is_online, status_data = check_api()
    st.session_state.api_status = is_online

    if is_online:
        st.markdown('<div class="status-box online">✅ Backend Online</div>', unsafe_allow_html=True)
        st.caption(f"Vector DB: {'Found' if status_data.get('vector_db_exists') else 'Not Found'}")
    else:
        st.markdown('<div class="status-box offline">❌ Backend Offline</div>', unsafe_allow_html=True)
        st.error("Please start main.py")

    # LLM Selection
    st.subheader("🤖 LLM Provider")
    model_type = st.radio(
        "Select Model:",
        ("auto", "google", "openai", "ollama"),
        index=0,
        help="Sent to API to select provider"
    )

    st.markdown("---")
    st.info(f"Connecting to: `{API_BASE_URL}`")

# --- MAIN PAGE ---
st.title("🤖 Autonomous QA Agent")
st.markdown("Generative AI Agent for Test Planning & Automation")

if not st.session_state.api_status:
    st.warning("⚠️ The FastAPI backend is unreachable. Please run `python app/main.py` in a separate terminal.")

# Create Tabs
tab1, tab2, tab3 = st.tabs(["📚 1. Knowledge Base", "📝 2. Test Planning", "💻 3. Code & Execute"])

# --- TAB 1: KNOWLEDGE BASE ---
with tab1:
    st.header("Build Knowledge Base")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload Spec files (PDF, MD, TXT, JSON)",
            accept_multiple_files=True,
            type=['pdf', 'md', 'txt', 'json', 'html']
        )

        # Note: We save files locally so the API (running locally) can find them in /data
        if uploaded_files:
            os.makedirs("data", exist_ok=True)
            for file in uploaded_files:
                file_path = os.path.join("data", file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
            st.success(f"Saved {len(uploaded_files)} files to ./data folder")

    with col2:
        st.subheader("Trigger Processing")
        force_rebuild = st.checkbox("Force Full Rebuild (Delete old DB)", value=False)

        if st.button("🧠 Ingest via API", disabled=not st.session_state.api_status):
            with st.spinner("Sending ingest request to API..."):
                try:
                    payload = {"data_path": "data", "force_rebuild": force_rebuild}
                    resp = requests.post(f"{API_BASE_URL}/ingest", json=payload)

                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.kb_built = True
                        st.balloons()
                        st.success(data["message"])
                        st.metric("Chunks Processed", data.get("chunks_count", 0))
                    else:
                        st.error(f"API Error: {resp.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# --- TAB 2: TEST PLANNING ---
with tab2:
    st.header("Generate Test Plan")

    query = st.text_area("Describe the testing scope:",
                         value="Generate comprehensive test cases for the checkout flow, focusing on validation and negative scenarios.",
                         height=100)

    if st.button("📝 Generate Test Cases", disabled=not st.session_state.api_status):
        with st.spinner("Waiting for API response..."):
            try:
                payload = {
                    "query": query,
                    "model_type": model_type,
                    "k_context": 5
                }
                resp = requests.post(f"{API_BASE_URL}/generate/tests", json=payload)

                if resp.status_code == 200:
                    result = resp.json()
                    st.session_state.test_cases = result.get("test_cases", [])
                    st.success(f"Received {len(st.session_state.test_cases)} test cases.")
                else:
                    st.error(f"API Error: {resp.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    # Display Test Cases
    if st.session_state.test_cases:
        st.divider()
        st.subheader("Test Plan Preview")
        for tc in st.session_state.test_cases:
            with st.expander(f"📌 {tc.get('id', 'TC')} - {tc.get('title', 'No Title')}"):
                st.write(tc)

# --- TAB 3: CODE GENERATION & EXECUTION ---
with tab3:
    st.header("Selenium Automation")

    if not st.session_state.test_cases:
        st.info("Please generate a test plan in Step 2 first.")
    else:
        # 1. Select Test Case
        tc_options = {f"{tc.get('id')} - {tc.get('title')}": tc for tc in st.session_state.test_cases}
        selected_key = st.selectbox("Select Test Case to Automate:", options=list(tc_options.keys()))
        selected_tc = tc_options[selected_key]

        # 2. HTML Context
        html_input_method = st.radio("HTML Source:", ("Auto (Server default)", "Paste Manually"))
        html_content = ""

        if html_input_method == "Paste Manually":
            html_content = st.text_area("Paste Raw HTML here:", height=150)

        # 3. Generate Button
        if st.button("💻 Generate Script via API", disabled=not st.session_state.api_status):
            with st.spinner("Requesting code from API..."):
                try:
                    payload = {
                        "test_case": selected_tc,
                        "html_content": html_content if html_content else None,
                        "model_type": model_type
                    }
                    resp = requests.post(f"{API_BASE_URL}/generate/code", json=payload)

                    if resp.status_code == 200:
                        st.session_state.generated_script = resp.json().get("code", "")
                        st.success("Script received!")
                    else:
                        st.error(f"API Error: {resp.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

        # 4. Code Editor & Execution
        if st.session_state.generated_script:
            st.divider()
            col_code, col_run = st.columns([2, 1])

            with col_code:
                st.subheader("Generated Python Code")
                final_code = st.text_area("Review Code:", value=st.session_state.generated_script, height=400)
                st.session_state.generated_script = final_code

            with col_run:
                st.subheader("Local Execution")
                st.markdown("Run the script on *this* machine to see the browser.")

                if st.button("▶️ Run Locally", type="primary"):
                    temp_script = "temp_runner.py"
                    with open(temp_script, "w") as f:
                        f.write(st.session_state.generated_script)

                    status_placeholder = st.empty()
                    status_placeholder.info("Running Selenium...")

                    try:
                        # Executing locally using subprocess
                        process = subprocess.run(
                            [sys.executable, temp_script],
                            capture_output=True, text=True, timeout=60
                        )

                        if process.returncode == 0:
                            status_placeholder.success("✅ Test Passed!")
                            st.balloons()
                        else:
                            status_placeholder.error("❌ Test Failed!")

                        with st.expander("Logs", expanded=True):
                            st.code(process.stdout + "\n" + process.stderr)

                    except Exception as e:
                        status_placeholder.error(f"Error: {e}")
                    finally:
                        if os.path.exists(temp_script):
                            os.remove(temp_script)
# import streamlit as st
# import os
# import sys
# import json
# import subprocess
# import time
# from pathlib import Path
# from dotenv import load_dotenv
#
# # --- SETUP PATHS ---
# # Add the current directory to sys.path to find 'app' modules
# sys.path.append(str(Path(__file__).parent))
# load_dotenv()
# try:
#     # Import logic from your existing backend files
#     # Ensure app/rag_engine.py exists with the functions we defined previously
#     from app.rag_engine import ingest_knowledge_base, generate_test_plan, generate_selenium_code
#     from app.utils import clean_python_code
# except ImportError as e:
#     st.error(f"❌ Critical Error: Could not import backend modules. Make sure 'app/rag_engine.py' exists. Details: {e}")
#     st.stop()
#
# # --- PAGE CONFIG ---
# st.set_page_config(
#     page_title="AutoQA Agent",
#     page_icon="🤖",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )
#
# # --- SESSION STATE INITIALIZATION ---
# if "test_cases" not in st.session_state:
#     st.session_state.test_cases = []
# if "generated_script" not in st.session_state:
#     st.session_state.generated_script = ""
# if "kb_built" not in st.session_state:
#     st.session_state.kb_built = False
#
# # --- CSS STYLING ---
# st.markdown("""
# <style>
#     .stButton>button {
#         width: 100%;
#         border-radius: 5px;
#     }
#     .success-box {
#         padding: 1rem;
#         background-color: #d4edda;
#         color: #155724;
#         border-radius: 5px;
#         margin-bottom: 1rem;
#     }
# </style>
# """, unsafe_allow_html=True)
#
# # --- SIDEBAR: CONFIGURATION ---
# with st.sidebar:
#     st.image("https://img.icons8.com/clouds/200/robot.png", width=100)
#     st.title("⚙️ Configuration")
#
#     # LLM Selection
#     st.subheader("🤖 LLM Provider")
#     model_type = st.radio(
#         "Select Model:",
#         ("auto", "google", "openai", "ollama"),
#         index=0,
#         help="Auto tries Google -> OpenAI -> Ollama"
#     )
#
#     # API Key Status
#     st.subheader("🔑 API Keys")
#     google_key = os.getenv("GOOGLE_API_KEY")
#     openai_key = os.getenv("OPENAI_API_KEY")
#
#     if google_key:
#         st.caption("✅ GOOGLE_API_KEY detected")
#     else:
#         st.caption("❌ GOOGLE_API_KEY missing")
#
#     if openai_key:
#         st.caption("✅ OPENAI_API_KEY detected")
#     else:
#         st.caption("❌ OPENAI_API_KEY missing")
#
#     st.markdown("---")
#     st.info("Files are saved to `/data` folder.")
#
# # --- MAIN PAGE ---
# st.title("🤖 Autonomous QA Agent")
# st.markdown("Generative AI Agent for Test Planning & Automation")
#
# # Create Tabs for Workflow
# tab1, tab2, tab3 = st.tabs(["📚 1. Knowledge Base", "📝 2. Test Planning", "💻 3. Code & Execute"])
#
# # --- TAB 1: KNOWLEDGE BASE ---
# with tab1:
#     st.header("Build Knowledge Base")
#
#     col1, col2 = st.columns(2)
#
#     with col1:
#         st.subheader("Upload Documents")
#         uploaded_files = st.file_uploader(
#             "Upload Spec files (PDF, MD, TXT, JSON)",
#             accept_multiple_files=True,
#             type=['pdf', 'md', 'txt', 'json', 'html']
#         )
#
#         if uploaded_files:
#             # Save files to data directory
#             os.makedirs("data", exist_ok=True)
#             for file in uploaded_files:
#                 file_path = os.path.join("data", file.name)
#                 with open(file_path, "wb") as f:
#                     f.write(file.getbuffer())
#             st.success(f"Saved {len(uploaded_files)} files to /data")
#
#     with col2:
#         st.subheader("Process Data")
#         force_rebuild = st.checkbox("Force Full Rebuild (Delete old DB)", value=False)
#
#         if st.button("🧠 Ingest & Vectorize"):
#             with st.spinner("Chunking documents and building Vector DB..."):
#                 try:
#                     result = ingest_knowledge_base(force_rebuild=force_rebuild)
#                     if result["success"]:
#                         st.session_state.kb_built = True
#                         st.balloons()
#                         st.success(result["message"])
#                         st.metric("Chunks Created", result.get("chunks", 0))
#                     else:
#                         st.error(result["message"])
#                 except Exception as e:
#                     st.error(f"Error: {str(e)}")
#
# # --- TAB 2: TEST PLANNING ---
# with tab2:
#     st.header("Generate Test Plan")
#
#     # Context check
#     if not st.session_state.kb_built and not os.path.exists("chroma_db_store"):
#         st.warning("⚠️ Warning: Knowledge base not detected. Please complete Step 1 first.")
#
#     query = st.text_area("Describe the testing scope:", value="Generate comprehensive test cases for the checkout flow, focusing on validation and negative scenarios.", height=100)
#
#     if st.button("📝 Generate Test Cases"):
#         with st.spinner(f"Consulting {model_type} to write test plan..."):
#             result = generate_test_plan(query=query, model_type=model_type)
#
#             if result["success"]:
#                 st.session_state.test_cases = result["test_cases"]
#                 st.success(f"Generated {len(result['test_cases'])} test cases.")
#             else:
#                 st.error(result["message"])
#
#     # Display Test Cases
#     if st.session_state.test_cases:
#         st.divider()
#         st.subheader("Test Plan Preview")
#
#         for i, tc in enumerate(st.session_state.test_cases):
#             with st.expander(f"📌 {tc.get('id', 'TC')} - {tc.get('title', 'No Title')}"):
#                 st.markdown(f"**Description:** {tc.get('description')}")
#                 st.markdown(f"**Expected Result:** {tc.get('expected_result')}")
#                 st.caption(f"Source: {tc.get('source_document')}")
#
# # --- TAB 3: CODE GENERATION & EXECUTION ---
# with tab3:
#     st.header("Selenium Automation")
#
#     if not st.session_state.test_cases:
#         st.info("Please generate a test plan in Step 2 first.")
#     else:
#         # 1. Select Test Case
#         tc_options = {f"{tc.get('id')} - {tc.get('title')}": tc for tc in st.session_state.test_cases}
#         selected_key = st.selectbox("Select Test Case to Automate:", options=list(tc_options.keys()))
#         selected_tc = tc_options[selected_key]
#
#         # 2. HTML Context
#         html_input_method = st.radio("HTML Source:", ("Auto (from /data/checkout.html)", "Paste Manually"))
#         html_content = None
#
#         if html_input_method == "Paste Manually":
#             html_content = st.text_area("Paste Raw HTML here:", height=150)
#
#         # 3. Generate Button
#         if st.button("💻 Generate Selenium Script"):
#             with st.spinner("Writing Python code..."):
#                 result = generate_selenium_code(
#                     test_case_json=selected_tc,
#                     html_content=html_content,
#                     model_type=model_type
#                 )
#
#                 if result["success"]:
#                     st.session_state.generated_script = result["code"]
#                     st.success("Script generated successfully!")
#                 else:
#                     st.error(result["message"])
#
#         # 4. Code Editor & Execution
#         if st.session_state.generated_script:
#             st.divider()
#             col_code, col_run = st.columns([2, 1])
#
#             with col_code:
#                 st.subheader("Generated Python Code")
#                 # Allow user to edit code before running
#                 final_code = st.text_area("Review Code:", value=st.session_state.generated_script, height=400)
#                 st.session_state.generated_script = final_code
#
#             with col_run:
#                 st.subheader("Execution")
#                 st.markdown("Ready to run this script locally.")
#
#                 if st.button("▶️ Run Test Script", type="primary"):
#                     # Save to temporary file
#                     temp_script = "temp_test_runner.py"
#                     with open(temp_script, "w") as f:
#                         f.write(st.session_state.generated_script)
#
#                     status_placeholder = st.empty()
#                     status_placeholder.info("Running Selenium... Browser may open.")
#
#                     try:
#                         # Run the script as a subprocess
#                         process = subprocess.run(
#                             [sys.executable, temp_script],
#                             capture_output=True,
#                             text=True,
#                             timeout=60
#                         )
#
#                         if process.returncode == 0:
#                             status_placeholder.success("✅ Test Passed!")
#                             st.balloons()
#                         else:
#                             status_placeholder.error("❌ Test Failed!")
#
#                         with st.expander("View Execution Logs", expanded=True):
#                             st.code(process.stdout + "\n" + process.stderr)
#
#                     except subprocess.TimeoutExpired:
#                         status_placeholder.error("❌ Execution Timed Out (60s)")
#                     except Exception as e:
#                         status_placeholder.error(f"❌ Execution Error: {e}")
#                     finally:
#                         if os.path.exists(temp_script):
#                             os.remove(temp_script)