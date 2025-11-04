# LLM-SLM Router

Intelligent routing system that automatically selects between Large Language Models (LLMs) and Small Language Models (SLMs) based on task complexity, cost, and performance requirements.

## Features

- Automatic model selection based on task complexity
- Hybrid orchestration with LLM/SLM fallback
- Cost and latency optimization
- Beautiful React + TypeScript frontend
- Real-time model selection visualization
- Ollama-first design (local, free)
- Optional Gemini API support

## Installation

### Backend

```bash
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Setup

### Ollama (Required)

Install Ollama from [ollama.ai](https://ollama.ai) and pull the required models:
```bash
ollama pull llama3
ollama pull llama3.2
```

Make sure Ollama is running:
```bash
ollama serve
```

### Gemini (Optional - Fallback/Alternative)

The API key is already set in `config.yaml`. To use Gemini instead of Ollama, change the `provider` in the `llm` or `slm` section to `"gemini"`.

## Usage

### Start Backend API

```bash
python main.py
```

The API will run on `http://localhost:8000`

### Start Frontend

```bash
cd frontend
npm run dev
```

The frontend will run on `http://localhost:3000`

### Run Examples (CLI)

```bash
python example.py
```

## Configuration

Edit `config.yaml` to configure model endpoints and routing parameters. Default uses Ollama for both LLM and SLM. To use Gemini, change the `provider` in the `llm` section to `"gemini"`.

