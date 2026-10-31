from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import json
from core_engine import analyze_full_github_repo_stream, chat_with_codebase

app = FastAPI(title="Repo Visualizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 MULTI-SESSION IN-MEMORY STATE
# Ab session_id ke hisaab se alag-alag repo context save honge
sessions = {}

class RepoRequest(BaseModel):
    url: str
    session_id: str

class ChatRequest(BaseModel):
    query: str
    session_id: str

@app.post("/api/analyze")
def analyze_repo(request: RepoRequest):
    if not request.url:
        raise HTTPException(status_code=400, detail="Repository URL is required")
    
    # Naya session banalo agar nahi hai
    if request.session_id not in sessions:
        sessions[request.session_id] = {"context": "", "history": []}
    
    def stream_and_save_context():
        for chunk in analyze_full_github_repo_stream(request.url):
            try:
                data = json.loads(chunk.strip())
                if data.get("type") == "done":
                    # Sirf is specific session_id ki memory update karo
                    sessions[request.session_id]["context"] = data.get("context", "")
                    sessions[request.session_id]["history"] = []
            except Exception:
                pass
            yield chunk

    return StreamingResponse(stream_and_save_context(), media_type="text/event-stream")

@app.post("/api/chat")
def chat_repo(request: ChatRequest):
    session = sessions.get(request.session_id)
    if not session or not session["context"]:
        raise HTTPException(status_code=400, detail="No active context for this session.")
        
    ai_reply = chat_with_codebase(request.query, session["context"], session["history"])
    
    session["history"].append({"role": "user", "content": request.query})
    session["history"].append({"role": "ai", "content": ai_reply})
    
    return {"reply": ai_reply}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)