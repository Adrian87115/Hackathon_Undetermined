from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Python.eco_gpt import ECOGPT
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

    #req.text jest string



    # time.sleep(2)
    # reponse = f"{req.text} changed"

    model = ECOGPT(checkpoint="/home/norbert/Hackathon_Undetermined/eco_gpt_20.pth", batch_size = 32, sequence_length = 64)

    output = model.generateResponse(req.text)

    print(output)
    return {"received": output}



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
    print("prompt sent")
    response = client.chat.completions.create(
        model=req.model,
        messages=[m.dict() for m in req.messages]
    )
    print("response sent")
    print(response)
    # Return EXACT same shape as OpenAI API so frontend doesn’t change
    return response
