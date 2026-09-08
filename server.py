from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import your actual function from step2.py
from step2 import ask_hx_agent 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    prompt: str

@app.post("/api/ask-hx")
async def ask_agent(query: Query):
    try:
        # Pass the website text to your Python script
        ai_reply = ask_hx_agent(query.prompt) 
        
        # Return the successful response back to the website
        return {"status": "success", "response": ai_reply}
        
    except Exception as e:
        # If something crashes in step2.py, catch it and send the error to the frontend
        print(f"[Error in Server] {e}")
        raise HTTPException(status_code=500, detail=str(e))