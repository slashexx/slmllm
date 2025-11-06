from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from orchestrator import HybridOrchestrator
import uuid
import json
import os
import pandas as pd
from datetime import datetime
import io
from datasets import load_dataset
import asyncio
import base64


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
            "/train/starcoder/languages": "GET - Get available StarCoder dataset languages",
            "/train/starcoder/download": "POST - Download and convert StarCoder dataset to CSV",
            "/train/starcoder/create": "POST - Create training job directly from StarCoder dataset",
            "/health": "GET - Health check"
        }
    }


@app.post("/train")
async def train(
    model: str = Form(...),
    dataset: Optional[UploadFile] = File(None),
    use_starcoder: Optional[bool] = Form(False),
    starcoder_language: Optional[str] = Form(None),
    starcoder_max_samples: Optional[int] = Form(10000)
):
    """
    Start a LoRA training job using Google Colab.
    Supports both CSV upload and StarCoder dataset from Hugging Face.
    """
    try:
        job_id = str(uuid.uuid4())
        dataset_path = None
        dataset_filename = None
        
        # Check if using StarCoder dataset or CSV upload
        if use_starcoder:
            if not starcoder_language:
                raise HTTPException(status_code=400, detail="StarCoder language is required when use_starcoder is true")
            
            # For StarCoder, we don't download - Colab will load it directly
            dataset_filename = f"starcoder_{starcoder_language}_{starcoder_max_samples}.parquet"
            
            # Create training job record with StarCoder parameters
            training_jobs[job_id] = {
                "job_id": job_id,
                "model": model,
                "dataset_type": "starcoder",
                "starcoder_language": starcoder_language,
                "starcoder_max_samples": starcoder_max_samples,
                "dataset_filename": dataset_filename,
                "status": "pending",
                "progress": 0,
                "created_at": datetime.now().isoformat(),
            }
        else:
            # Traditional CSV upload
            if not dataset:
                raise HTTPException(status_code=400, detail="Either upload a CSV file or use StarCoder dataset")
            
            if not dataset.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail="Only CSV files are supported")
            
            # Read the dataset
            contents = await dataset.read()
            
            # Validate file size (max 50MB for base64 storage)
            if len(contents) > 50 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Dataset file too large. Maximum size is 50MB. Please use StarCoder dataset for larger datasets.")
            
            # Store dataset content as base64 in job record (so it persists in serverless)
            dataset_content_b64 = base64.b64encode(contents).decode('utf-8')
            dataset_filename = dataset.filename
            
            # Also try to save to /tmp as fallback (for local dev)
            dataset_path = f"/tmp/{job_id}_{dataset.filename}"
            try:
                os.makedirs("/tmp", exist_ok=True)
                with open(dataset_path, "wb") as f:
                    f.write(contents)
            except Exception as e:
                print(f"Warning: Could not save to /tmp: {e}")
                dataset_path = None
            
            # Create training job record with dataset content stored
            training_jobs[job_id] = {
                "job_id": job_id,
                "model": model,
                "dataset_type": "csv",
                "dataset_filename": dataset_filename,
                "dataset_content_b64": dataset_content_b64,  # Store actual content
                "dataset_path": dataset_path,  # Fallback for local dev
                "status": "pending",
                "progress": 0,
                "created_at": datetime.now().isoformat(),
            }
        
        # Generate Colab notebook URL with parameters
        # Pass all parameters via URL
        params = f"job_id={job_id}&model={model}"
        if use_starcoder:
            params += f"&use_starcoder=true&starcoder_language={starcoder_language}&starcoder_max_samples={starcoder_max_samples}"
        
        colab_url = f"https://colab.research.google.com/github/slashexx/lora-fine-pipe/blob/main/lora_training.ipynb?{params}"
        
        training_jobs[job_id]["colab_url"] = colab_url
        
        return {
            "job_id": job_id,
            "colab_url": colab_url,
            "message": "Training job created! Click the Colab link below. When the notebook opens, click 'Runtime > Run all' in the menu to start training automatically.",
            "instructions": [
                "1. Click the Colab link below to open the notebook",
                "2. When the notebook opens, click 'Runtime' > 'Run all' from the top menu",
                "3. The notebook will automatically install packages, load your dataset, and start training",
                "4. Training progress will be tracked in real-time",
                "5. Your trained model will be saved when complete"
            ],
            "dataset_type": "starcoder" if use_starcoder else "csv"
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
    Only works for CSV uploads, not StarCoder (which loads directly in Colab).
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    job = training_jobs[job_id]
    
    if job.get("dataset_type") == "starcoder":
        raise HTTPException(
            status_code=400, 
            detail="StarCoder dataset is loaded directly in Colab from Hugging Face. No download needed."
        )
    
    # Try to get dataset from base64 content first (most reliable)
    dataset_content_b64 = job.get("dataset_content_b64")
    if dataset_content_b64:
        try:
            dataset_content = base64.b64decode(dataset_content_b64)
            return Response(
                content=dataset_content,
                media_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{job.get("dataset_filename", "dataset.csv")}"'}
            )
        except Exception as e:
            print(f"Error decoding base64 dataset: {e}")
    
    # Fallback to file path (for local dev)
    dataset_path = job.get("dataset_path")
    if dataset_path and os.path.exists(dataset_path):
        return FileResponse(
            path=dataset_path,
            media_type="text/csv",
            filename=job.get("dataset_filename", "dataset.csv")
        )
    
    raise HTTPException(status_code=404, detail="Dataset file not found")


@app.get("/train/starcoder/languages")
async def get_starcoder_languages():
    """
    Get list of available programming languages in StarCoder dataset.
    """
    # Common programming languages available in StarCoder dataset
    languages = [
        "python", "javascript", "java", "cpp", "c", "go", "rust", "typescript",
        "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "shell",
        "powershell", "perl", "lua", "dart", "haskell", "ocaml", "clojure",
        "erlang", "elixir", "fsharp", "vb", "csharp", "html", "css", "sql",
        "json", "yaml", "xml", "markdown", "dockerfile", "makefile", "cmake"
    ]
    
    return {
        "languages": sorted(languages),
        "message": "Available programming languages in StarCoder dataset. Use 'python' for Python code."
    }


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

