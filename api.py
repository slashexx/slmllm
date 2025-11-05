from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from orchestrator import HybridOrchestrator
import uuid
import json
import os
from datetime import datetime


app = FastAPI(title="LLM-SLM Router API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://slmllm.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = HybridOrchestrator()

# In-memory storage for training jobs (in production, use a database)
training_jobs = {}


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


class DistillRequest(BaseModel):
    prompt: str


class DistillResponse(BaseModel):
    response: str
    model_used: str
    refined_prompt: str
    original_prompt: str
    distillation_used: bool
    distillation_error: Optional[str] = None


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


@app.post("/distill", response_model=DistillResponse)
async def distill(request: DistillRequest):
    try:
        result = orchestrator.distill_and_process(request.prompt)
        return DistillResponse(
            response=result["response"],
            model_used=result["model_used"],
            refined_prompt=result["refined_prompt"],
            original_prompt=result["original_prompt"],
            distillation_used=result["distillation_used"],
            distillation_error=result.get("distillation_error")
        )
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"Error processing distillation: {error_detail}")
        print(f"Traceback: {traceback_str}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/")
async def root():
    return {
        "message": "LLM-SLM Router API",
        "endpoints": {
            "/query": "POST - Process a query with intelligent routing",
            "/distill": "POST - Distill prompt with SLM then process with LLM",
            "/train": "POST - Start LoRA training job with Google Colab",
            "/train/status/{job_id}": "GET - Get training job status",
            "/train/dataset/{job_id}": "GET - Download training dataset",
            "/train/update/{job_id}": "POST - Update training job status (from Colab)",
            "/health": "GET - Health check"
        }
    }


@app.post("/train")
async def train(
    model: str = Form(...),
    dataset: UploadFile = File(...)
):
    """
    Start a LoRA training job using Google Colab.
    """
    try:
        # Validate file type
        if not dataset.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read the dataset
        contents = await dataset.read()
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Store dataset temporarily (in production, use cloud storage)
        dataset_path = f"/tmp/{job_id}_{dataset.filename}"
        with open(dataset_path, "wb") as f:
            f.write(contents)
        
        # Generate Colab notebook URL with parameters
        # This will be a template that the user can run
        colab_url = f"https://colab.research.google.com/github/slashexx/lora-fine-pipe/blob/main/lora_training.ipynb?job_id={job_id}&model={model}"
        
        # Create training job record
        training_jobs[job_id] = {
            "job_id": job_id,
            "model": model,
            "dataset_filename": dataset.filename,
            "dataset_path": dataset_path,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "colab_url": colab_url
        }
        
        return {
            "job_id": job_id,
            "colab_url": colab_url,
            "message": "Training job created. Click the Colab link to start training on Google's GPUs."
        }
        
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"Error creating training job: {error_detail}")
        print(f"Traceback: {traceback_str}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/train/status/{job_id}")
async def get_training_status(job_id: str):
    """
    Get the status of a training job.
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    return training_jobs[job_id]


@app.get("/train/dataset/{job_id}")
async def get_training_dataset(job_id: str):
    """
    Download the dataset file for a training job.
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    dataset_path = training_jobs[job_id].get("dataset_path")
    
    if not dataset_path or not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")
    
    return FileResponse(
        path=dataset_path,
        media_type="text/csv",
        filename=training_jobs[job_id].get("dataset_filename", "dataset.csv")
    )


@app.post("/train/update/{job_id}")
async def update_training_status(
    job_id: str,
    status: str = Form(...),
    progress: int = Form(0),
    error: Optional[str] = Form(None)
):
    """
    Update training job status (called from Colab notebook).
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    training_jobs[job_id]["status"] = status
    training_jobs[job_id]["progress"] = progress
    training_jobs[job_id]["updated_at"] = datetime.now().isoformat()
    
    if error:
        training_jobs[job_id]["error"] = error
    
    if status == "completed":
        training_jobs[job_id]["completed_at"] = datetime.now().isoformat()
    
    return {"message": "Status updated successfully"}

