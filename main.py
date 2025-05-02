from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
import ast
import os

# Load API key from .env
load_dotenv()
# Initialize OpenAI client
client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY")
)

# Generate a docstring using OpenAI LLM (NumPy + PEP 257 style)
def generate_docstring(code_snippet: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo", # USE DIFFERENT MODEL TO AVOID PLAN AND BILLING DETAILS
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert Python assistant. "
                        "Write a concise, complete Python docstring following PEP 257 and NumPy style. "
                        "Include 'Args' and 'Returns' sections if applicable."
                    )
                },
                {
                    "role": "user",
                    "content": f"Here is a function:\n\n{code_snippet}\n\nWrite the docstring only."
                }
            ],
            temperature=0.2
        )
        return completion.choices[0].message.content.strip()
    except RateLimitError:
        print("Rate limit exceeded. Please try again later.")

# Get source code for an AST node
def get_function_source(source_code, node):
    return ast.get_source_segment(source_code, node)

# Check for existing docstring
def has_docstring(node):
    return (
        isinstance(node.body[0], ast.Expr) and
        isinstance(getattr(node.body[0], "value", None), (ast.Str, ast.Constant))
    )

# Extract all function/class definitions from source code
def extract_definitions(source_code):
    tree = ast.parse(source_code)
    return [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))
    ]

# TESTING GROUNDS
if __name__ == "__main__":
    filename = "test_script.py"

    with open(filename, "r") as file:
        source = file.read()

    definitions = extract_definitions(source)

    for node in definitions:
        if not has_docstring(node):
            func_code = get_function_source(source, node)
            print(f"\nFunction: {node.name}")
            docstring = generate_docstring(func_code)
            if docstring is not None:
                print("Generated Docstring:\n" + docstring)
            else:
                print(f"Failed to generate docstring for function: {node.name}")
