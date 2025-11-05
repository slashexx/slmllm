# 🎯 LoRA Training Integration Guide

This guide explains how to use the automated LoRA training feature with Google Colab integration.

## Overview

The LoRA training feature allows users to:
- Select a base model from a curated list
- Upload a custom CSV dataset
- Train a LoRA adapter automatically on Google Colab's free GPU
- Track training progress in real-time
- Download the trained model adapter

## How It Works

### Frontend Flow
1. User selects a model from the dropdown
2. User uploads a CSV dataset with `input` and `output` columns
3. System creates a training job and generates a Colab notebook link
4. User clicks the Colab link to start training on Google's infrastructure
5. Training progress is tracked and displayed in the UI

### Backend Flow
1. API receives model selection and dataset
2. Creates a unique job ID and stores dataset
3. Generates a parametrized Colab notebook URL
4. Returns job ID and Colab URL to frontend
5. Provides status endpoint for progress tracking

### Colab Training Flow
1. Notebook loads with job parameters
2. Installs required packages (transformers, PEFT, etc.)
3. Downloads dataset from backend
4. Configures 4-bit quantization for memory efficiency
5. Sets up LoRA configuration
6. Trains the model with specified parameters
7. Updates training status via API callbacks
8. Saves trained adapter for download

## Dataset Format

Your CSV file should have at least two columns:
- `input`: The input text/prompt
- `output`: The expected output/response

Example:
```csv
input,output
"What is machine learning?","Machine learning is a subset of AI that enables systems to learn from data."
"Explain neural networks","Neural networks are computational models inspired by the human brain."
```

## Available Models

- **Llama 2 7B** - Meta's powerful 7B parameter model
- **Llama 2 13B** - Larger variant with better performance
- **Mistral 7B** - High-performance 7B model
- **Phi-2** - Microsoft's efficient small model
- **Gemma 7B** - Google's Gemini-based model
- **TinyLlama 1.1B** - Very small, fast model

## LoRA Configuration

Default LoRA settings:
- **Rank (r)**: 16
- **Alpha**: 32
- **Target modules**: q_proj, k_proj, v_proj, o_proj
- **Dropout**: 0.05
- **Training epochs**: 3
- **Learning rate**: 2e-4

## API Endpoints

### Start Training Job
```bash
POST /api/train
Content-Type: multipart/form-data

Fields:
- model: string (model identifier)
- dataset: file (CSV file)

Response:
{
  "job_id": "uuid",
  "colab_url": "https://colab.research.google.com/...",
  "message": "Training job created..."
}
```

### Get Training Status
```bash
GET /api/train/status/{job_id}

Response:
{
  "job_id": "uuid",
  "model": "llama-2-7b",
  "status": "training",
  "progress": 45,
  "colab_url": "...",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:05:00"
}
```

### Update Training Status (Called from Colab)
```bash
POST /api/train/update/{job_id}
Content-Type: application/x-www-form-urlencoded

Fields:
- status: string (pending|training|completed|failed)
- progress: int (0-100)
- error: string (optional)
```

## Deployment Considerations

### Using Google Colab
**Advantages:**
- Free GPU access (T4 GPU on free tier)
- No server compute costs
- Easy for users to monitor training
- Can use Colab Pro for faster GPUs

**Limitations:**
- Requires manual notebook execution
- Session timeouts (12 hours on free tier)
- Not fully automated
- User needs Google account

### Alternative: Serverless GPU
For production, consider:
- **Modal** - Serverless GPU functions
- **RunPod** - On-demand GPU instances
- **Lambda Labs** - Affordable GPU cloud
- **Vast.ai** - Decentralized GPU marketplace

### Production Database
Replace in-memory storage with:
```python
# Instead of:
training_jobs = {}

# Use:
from motor.motor_asyncio import AsyncIOMotorClient
db = AsyncIOMotorClient(MONGO_URI).training_db
```

## Usage Example

```python
import requests

# Upload dataset and start training
files = {'dataset': open('my_data.csv', 'rb')}
data = {'model': 'llama-2-7b'}

response = requests.post(
    'https://slmllm-backend.vercel.app/api/train',
    data=data,
    files=files
)

job = response.json()
print(f"Training job created: {job['job_id']}")
print(f"Open Colab: {job['colab_url']}")

# Check status
status = requests.get(
    f"https://slmllm-backend.vercel.app/api/train/status/{job['job_id']}"
)
print(status.json())
```

## Security Considerations

1. **File Upload Limits**: Implement size limits for CSV files
2. **Authentication**: Add API keys for production
3. **Rate Limiting**: Prevent abuse of training endpoints
4. **Dataset Storage**: Use secure cloud storage (S3, GCS)
5. **Job Cleanup**: Implement automatic cleanup of old jobs

## Future Enhancements

- [ ] Direct file upload to cloud storage
- [ ] Webhook notifications on training completion
- [ ] Model versioning and registry
- [ ] Automatic hyperparameter tuning
- [ ] Multi-GPU training support
- [ ] Integration with HuggingFace Hub
- [ ] Custom LoRA configuration UI
- [ ] Training cost estimation
- [ ] Model performance benchmarking

## Troubleshooting

### "Out of Memory" in Colab
- Use a smaller model (TinyLlama, Phi-2)
- Reduce batch size
- Enable gradient checkpointing
- Use 8-bit quantization instead of 4-bit

### Training Too Slow
- Upgrade to Colab Pro for better GPU
- Reduce number of epochs
- Decrease sequence length
- Use a smaller dataset for testing

### Dataset Format Errors
- Ensure CSV has 'input' and 'output' columns
- Check for proper encoding (UTF-8)
- Remove special characters if needed
- Validate data before upload

## Resources

- [PEFT Documentation](https://huggingface.co/docs/peft)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [Google Colab Guide](https://colab.research.google.com/)
- [Transformers Library](https://huggingface.co/docs/transformers)
