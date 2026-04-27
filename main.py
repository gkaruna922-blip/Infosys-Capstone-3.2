from fastapi import FastAPI, HTTPException
from models.schemas import ChatRequest, AgentResponse
from agents.orchestrator import orchestrator
import uvicorn
import traceback

app = FastAPI(title="AI Shopping Assistant API")

@app.get("/")
async def root():
    return {"message": "AI Shopping Assistant API is running"}

@app.post("/chat", response_model=AgentResponse)
async def chat(request: ChatRequest):
    try:
        response = await orchestrator.process_message(
            session_id=request.session_id,
            customer_id=request.customer_id,
            message=request.message,
            history = request.history
        )
        return response
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
