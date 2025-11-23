"""
Main entry point for the Autonomous QA Agent.
Run this file to start the Streamlit UI.
"""

import subprocess
import sys
import os
from pathlib import Path

if __name__ == "__main__":
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🚀 Starting Autonomous QA Agent...")
    print("📱 Opening Streamlit UI...")
    print(f"📂 Working directory: {project_root}")
    
    # Run streamlit with the project root in PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "app/ui.py"],
        env=env,
        cwd=project_root
    )

