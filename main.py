"""
Main entry point for the Autonomous QA Agent.
Run this file to start the Streamlit UI.
"""

import subprocess
import sys

if __name__ == "__main__":
    print("🚀 Starting Autonomous QA Agent...")
    print("📱 Opening Streamlit UI...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app/ui.py"])

