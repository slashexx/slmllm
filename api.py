from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from orchestrator import HybridOrchestrator


app = FastAPI(title="LLM-SLM Router API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = HybridOrchestrator()


class QueryRequest(BaseModel):
    prompt: str
    priority: Optional[str] = "balanced"
    use_llm_fallback: Optional[bool] = True


class QueryResponse(BaseModel):
    response: str
    model_used: str
    decision: dict
    fallback_used: bool
    fallback_reason: Optional[str] = None


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        result = orchestrator.process(
            request.prompt,
            priority=request.priority,
            use_llm_fallback=request.use_llm_fallback
        )
        
        decision_dict = {
            "model_type": result["decision"].model_type,
            "confidence": result["decision"].confidence,
            "reason": result["decision"].reason,
            "estimated_cost": result["decision"].estimated_cost,
            "estimated_latency": result["decision"].estimated_latency
        }
        
        return QueryResponse(
            response=result["response"],
            model_used=result["model_used"],
            decision=decision_dict,
            fallback_used=result["fallback_used"],
            fallback_reason=result.get("fallback_reason")
        )
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"Error processing query: {error_detail}")
        print(f"Traceback: {traceback_str}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {
        "message": "LLM-SLM Router API",
        "endpoints": {
            "/query": "POST - Process a query with intelligent routing",
            "/health": "GET - Health check"
        }
    }

