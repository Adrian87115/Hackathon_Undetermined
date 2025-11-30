from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import time

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

@app.post("/process")
def process_text(req: TextRequest):
    time.sleep(2)
    reponse = f"{req.text} changed"
    return {"received": reponse}



class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Main chat endpoint ---
@app.post("/chat")
def backend_chat(req: ChatRequest):
    """
    This endpoint receives the exact body your frontend sends,
    forwards it to OpenAI, and returns the OpenAI response unchanged.
    """
    response = client.chat.completions.create(
        model=req.model,
        messages=[m.dict() for m in req.messages]
    )

    # Return EXACT same shape as OpenAI API so frontend doesn’t change
    return response
