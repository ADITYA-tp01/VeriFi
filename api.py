import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from langgraph.types import Command

from agent.graph import app as agent_app

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    user_input: str
    thread_id: Optional[str] = None

class ResumeRequest(BaseModel):
    answer: str
    thread_id: str

def format_result(result: dict):
    # Remove binary data before returning to frontend
    if "qr_image" in result:
        del result["qr_image"]
    
    # Extract needed fields to pass back to frontend
    return {
        "status": "success",
        "result": result,
        "waiting_answer": result.get("__interrupt__")[0].value if result.get("__interrupt__") else None
    }

import traceback

@app.post("/api/analyze")
async def analyze(
    user_input: str = Form(""),
    thread_id: str = Form(""),
    qr_image: UploadFile = File(None)
):
    tid = thread_id if thread_id else str(uuid.uuid4())
    config = {"configurable": {"thread_id": tid}}
    
    payload = {"user_input": user_input}
    if qr_image:
        payload["qr_image"] = await qr_image.read()
        
    try:
        result = agent_app.invoke(payload, config)
        res = format_result(result)
        res["thread_id"] = tid
        return res
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resume")
async def resume(req: ResumeRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    try:
        result = agent_app.invoke(Command(resume=req.answer), config)
        res = format_result(result)
        res["thread_id"] = req.thread_id
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
