# HX Agent 🤖

HX is a lightweight, locally-hosted AI agent with a custom glassmorphism frontend. It connects a sleek web interface to a powerful Python backend, utilizing tool-calling to interact directly with local files and perform complex calculations.

## ✨ Features

* **Document Processing:** Reads and extracts text directly from local PDFs.
* **Data Handling:** Capable of reading and writing data to Excel (`.xlsx`) and CSV files within the project workspace.
* **Mathematical Operations:** Built-in calculation tool for evaluating complex mathematical expressions.
* **Custom UI:** Features a responsive, animated chat interface built with pure HTML, CSS, and vanilla JavaScript (no heavy frontend frameworks required).

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, OpenAI SDK (via OpenRouter/Groq).
* **Data Processing:** `pypdf`, `openpyxl`.
* **Frontend:** HTML5, CSS3 (CSS Variables, Flexbox), Vanilla JavaScript.

## 🚀 Quick Start

To run HX Agent locally, follow these steps:

1. **Clone the repository and install dependencies:**
   Ensure you have Python installed, then set up your environment:

   pip install fastapi uvicorn pydantic pypdf openpyxl openai python-dotenv


## Set up your environment variables:
Create a .env file in the root directory and add your API key (this file is git-ignored):

MODEL_NAME="your-model-name-here"
MODEL_API_KEY="your-api-key-here"


## Start the backend server:
Launch the FastAPI bridge to listen for the frontend:

uvicorn server:app --reload

## Launch the UI:
Open index.html using VS Code's Live Server (or just open the file in your browser). Type a prompt, hit send, and HX will handle the rest.