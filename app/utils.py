import json
import re
import os

def clean_llm_json(response_text: str):
    """
    Cleans the raw string response from the LLM to extract valid JSON.
    Removes markdown backticks ```json ... ``` if present.
    """
    # Remove leading/trailing whitespace
    text = response_text.strip()
    
    # Remove markdown code blocks if they exist
    if "```" in text:
        # Regex to capture content inside ```json ... ``` or just ``` ... ```
        pattern = r"```(?:json)?\s*(.*)\s*```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            text = match.group(1)
    
    # Attempt to parse to verify it is valid
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Error: {e}")
        print(f"Raw Text: {text}")
        return []

def clean_python_code(response_text: str):
    """
    Extracts pure Python code from LLM response, removing markdown formatting.
    """
    text = response_text.strip()
    
    # Remove markdown code blocks
    pattern = r"```(?:python)?\s*(.*)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        text = match.group(1)
        
    return text

def save_generated_script(filename: str, code: str):
    """
    Saves the Python code to the generated_scripts folder.
    Returns the absolute path to the saved file.
    """
    # Ensure directory exists
    output_dir = "generated_scripts"
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
    
    # Return absolute path to avoid path resolution issues
    return os.path.abspath(filepath)