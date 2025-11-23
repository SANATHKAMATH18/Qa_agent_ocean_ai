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
    Also fixes invalid escape sequences in HTML content strings.
    """
    text = response_text.strip()
    
    # Remove markdown code blocks
    pattern = r"```(?:python)?\s*(.*)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        text = match.group(1)
    
    # Fix invalid escape sequences in HTML content strings
    # Look for patterns like: HTML_CONTENT = """...""" or html_content = """..."""
    # and convert them to raw strings: HTML_CONTENT = r"""..."""
    # Match variable assignments with triple-quoted strings that likely contain HTML
    html_pattern = r'(\b\w+\s*=\s*)("""[\s\S]*?""")'
    
    def fix_html_string(match):
        var_assignment = match.group(1)
        html_string = match.group(2)
        # Check if it's already a raw string
        if not html_string.startswith('r"""') and not html_string.startswith("r'''"):
            # Check if the string contains HTML-like content (tags, attributes, etc.)
            # This is a heuristic - if it contains < and >, it's likely HTML
            if '<' in html_string and '>' in html_string:
                # Convert to raw string
                return f'{var_assignment}r{html_string}'
        return match.group(0)
    
    # Apply the fix
    text = re.sub(html_pattern, fix_html_string, text, flags=re.MULTILINE)
    
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