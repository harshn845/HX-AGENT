import os
import json
import math
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from pypdf import PdfReader
from openpyxl import load_workbook


# -----------------------------
# Load environment variables
# -----------------------------

load_dotenv()

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GOOGLE_API_KEY")
)

MODEL_NAME = os.getenv("MODEL_NAME")


# -----------------------------
# TOOLS
# -----------------------------

def list_files():
    """List files in the current project folder."""

    files = []

    for file in Path(".").iterdir():
        if file.is_file():
            files.append(file.name)

    return files


def read_pdf(file_path):
    """Read text from a PDF file."""

    path = Path(file_path)

    if not path.exists():
        return f"File not found: {file_path}"

    if path.suffix.lower() != ".pdf":
        return "That file is not a PDF."

    reader = PdfReader(path)

    text = ""

    for page_number, page in enumerate(reader.pages):
        page_text = page.extract_text()

        if page_text:
            text += f"\n--- Page {page_number + 1} ---\n"
            text += page_text

    return text


def read_excel(file_path):
    """Read an Excel workbook."""

    path = Path(file_path)

    if not path.exists():
        return f"File not found: {file_path}"

    if path.suffix.lower() not in [".xlsx", ".xlsm"]:
        return "Please provide an .xlsx or .xlsm file."

    workbook = load_workbook(path, data_only=True)

    result = {}

    for sheet_name in workbook.sheetnames:

        sheet = workbook[sheet_name]

        rows = []

        for row in sheet.iter_rows(values_only=True):
            rows.append(list(row))

        result[sheet_name] = rows

    return result


def write_excel(file_path, sheet_name, data):
    """Write data to an Excel spreadsheet."""

    path = Path(file_path)

    if path.exists():
        workbook = load_workbook(path)
    else:
        from openpyxl import Workbook
        workbook = Workbook()

    if sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
    else:
        sheet = workbook.create_sheet(sheet_name)

    for row in data:
        sheet.append(row)

    workbook.save(path)

    return f"Successfully wrote data to {file_path}, sheet: {sheet_name}"


def calculate(expression):
    """Calculate a mathematical expression."""

    allowed_names = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "pow": pow
    }

    try:
        result = eval(
            expression,
            {"__builtins__": {}},
            allowed_names
        )

        return str(result)

    except Exception as e:
        return f"Could not calculate expression: {e}"


# -----------------------------
# TOOL DEFINITIONS
# -----------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files available in the current project folder.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_pdf",
            "description": "Read and extract text from a PDF file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the PDF file."
                    }
                },
                "required": ["file_path"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_excel",
            "description": "Read data from an Excel workbook.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the Excel file."
                    }
                },
                "required": ["file_path"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "write_excel",
            "description": "Write rows of data into an Excel spreadsheet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string"
                    },
                    "sheet_name": {
                        "type": "string"
                    },
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "array"
                        }
                    }
                },
                "required": [
                    "file_path",
                    "sheet_name",
                    "data"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to calculate."
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


# -----------------------------
# TOOL EXECUTOR
# -----------------------------

def execute_tool(tool_name, arguments):

    if tool_name == "list_files":
        return list_files()

    elif tool_name == "read_pdf":
        return read_pdf(arguments["file_path"])

    elif tool_name == "read_excel":
        return read_excel(arguments["file_path"])

    elif tool_name == "write_excel":
        return write_excel(
            arguments["file_path"],
            arguments["sheet_name"],
            arguments["data"]
        )

    elif tool_name == "calculate":
        return calculate(arguments["expression"])

    else:
        return f"Unknown tool: {tool_name}"


# -----------------------------
# AGENT
# -----------------------------

messages = [
    {
        "role": "system",
        "content": """
You are a helpful AI agent.

You can use tools to work with files and perform calculations.

Available abilities:
- List files
- Read PDFs
- Read Excel files
- Write Excel files
- Perform calculations

When the user asks you to perform a task, decide whether you need a tool.

Do not pretend that you performed an action if you did not actually use a tool.

When working with files, use the tools provided.
"""
    }
]


# -----------------------------
# CHAT LOOP
# -----------------------------

# -----------------------------
# API INTEGRATION (Replaces old CHAT LOOP)
# -----------------------------

def ask_hx_agent(user_input):
    """
    Takes a prompt from the FastAPI backend, runs the AI loop, 
    and returns the final string response.
    """
    global messages # This keeps the chat history alive between requests

    # 1. Add the user's web prompt to the history
    messages.append({
        "role": "user",
        "content": user_input
    })

    # 2. Agent reasoning/tool loop
    while True:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # -------------------------
        # No tool needed - return the final answer to the website!
        # -------------------------
        if not message.tool_calls:
            reply = message.content

            messages.append({
                "role": "assistant",
                "content": reply
            })

            print("\n[Terminal Log] Agent:", reply)
            
            # 👇 INSTEAD OF break, WE RETURN THE REPLY TO FastAPI
            return reply 

        # -------------------------
        # Tool requested
        # -------------------------
        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # We keep this print statement so you can watch what it's doing in VS Code!
            print(f"\n[Terminal Log] Agent using tool: {tool_name}")

            result = execute_tool(tool_name, arguments)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, default=str)
            })

            #Use this for making a agentic AI