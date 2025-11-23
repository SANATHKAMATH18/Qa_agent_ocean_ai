from app.rag_engine import ingest_knowledge_base, generate_test_plan, generate_selenium_code
from app.utils import clean_python_code, save_generated_script

# 1. Build DB
print(ingest_knowledge_base())

# 2. Generate Plan
test_cases = generate_test_plan()
print(f"\nGenerated {len(test_cases)} Test Cases.")
print(test_cases[0]) # Print the first one to check structure

# 3. Generate Script for the first case
first_case = test_cases[0]
raw_code = generate_selenium_code(first_case)
clean_code = clean_python_code(raw_code)

# 4. Save it
saved_path = save_generated_script(f"{first_case['id']}.py", clean_code)
print(f"\nScript saved to: {saved_path}")