"""
Test Runner - Executes Selenium scripts and reports results
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List
import time

def run_selenium_script(script_path: str, timeout: int = 60) -> Dict:
    """
    Run a Selenium script and return pass/fail status.
    
    Args:
        script_path: Path to the Python Selenium script
        timeout: Maximum time to wait for script execution (seconds)
    
    Returns:
        Dict with status, message, and execution details
    """
    script_path = Path(script_path)
    
    # Convert to absolute path to avoid path resolution issues
    if not script_path.is_absolute():
        script_path = script_path.resolve()
    
    if not script_path.exists():
        return {
            "status": "error",
            "passed": False,
            "message": f"Script file not found: {script_path}",
            "error": "FileNotFoundError"
        }
    
    try:
        
        # Run the script
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=script_path.parent
        )
        execution_time = time.time() - start_time
        
        # Check exit code (0 = success, non-zero = failure)
        if result.returncode == 0:
            return {
                "status": "passed",
                "passed": True,
                "message": "Test passed successfully",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": round(execution_time, 2),
                "exit_code": result.returncode
            }
        else:
            return {
                "status": "failed",
                "passed": False,
                "message": f"Test failed with exit code {result.returncode}",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": round(execution_time, 2),
                "exit_code": result.returncode
            }
    
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "passed": False,
            "message": f"Test timed out after {timeout} seconds",
            "error": "TimeoutError"
        }
    except Exception as e:
        return {
            "status": "error",
            "passed": False,
            "message": f"Error running test: {str(e)}",
            "error": type(e).__name__
        }


def run_all_test_scripts(test_cases: List[Dict], scripts_dir: str = "generated_scripts") -> List[Dict]:
    """
    Run all generated Selenium scripts for the given test cases.
    
    Args:
        test_cases: List of test case dictionaries with 'id' field
        scripts_dir: Directory containing the generated scripts
    
    Returns:
        List of results for each test case
    """
    results = []
    scripts_path = Path(scripts_dir)
    
    for test_case in test_cases:
        tc_id = test_case.get("id", "unknown")
        script_filename = f"{tc_id}.py"
        script_path = scripts_path / script_filename
        
        result = {
            "test_case": test_case,
            "script_path": str(script_path),
            "script_exists": script_path.exists()
        }
        
        if script_path.exists():
            # Run the script
            execution_result = run_selenium_script(str(script_path))
            result.update(execution_result)
        else:
            result.update({
                "status": "not_found",
                "passed": False,
                "message": f"Script not found: {script_filename}"
            })
        
        results.append(result)
    
    return results


def generate_test_summary(results: List[Dict]) -> Dict:
    """
    Generate a summary report from test execution results.
    
    Args:
        results: List of test execution results
    
    Returns:
        Summary dictionary with statistics
    """
    total = len(results)
    passed = sum(1 for r in results if r.get("passed", False))
    failed = total - passed
    not_found = sum(1 for r in results if r.get("status") == "not_found")
    
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "not_found": not_found,
        "pass_rate": round((passed / total * 100) if total > 0 else 0, 2),
        "results": results
    }

