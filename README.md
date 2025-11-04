# LLM-SLM Router

Intelligent routing system that automatically selects between Large Language Models (LLMs) and Small Language Models (SLMs) based on task complexity, cost, and performance requirements.

## 🌟 Features

### Intelligent Model Routing
- **Complexity-based routing**: Automatically analyzes prompt complexity using heuristics (word count, technical terms, question patterns, etc.)
- **Token-aware routing**: Routes large inputs (2000+ tokens) directly to Gemini for speed and reliability
- **Smart thresholds**: Configurable thresholds for when to use SLM vs LLM vs Gemini
- **Priority modes**: Choose between Cost, Balanced, or Speed optimization

### Hybrid Orchestration
- **Automatic fallback**: If SLM fails or produces low-quality responses, automatically falls back to LLM
- **Gemini fallback**: If Ollama is unavailable, automatically uses Gemini API
- **Quality checks**: Validates response quality before accepting SLM output
- **Error handling**: Graceful error handling with automatic recovery

### Prompt Distillation
- **Two-stage processing**: Refines prompts using SLM first, then processes with LLM
- **Cost optimization**: Uses cheaper SLM to optimize prompts before sending to expensive LLM
- **Quality improvement**: Better, more focused prompts lead to better LLM responses
- **Visual feedback**: See both the refined prompt and final response

### Smart Gemini Integration
- **Automatic routing**: Large inputs (1000+ tokens) automatically routed to Gemini
- **High-complexity routing**: Complex tasks prefer Gemini for reliability
- **Speed optimization**: Gemini preferred for fast, reliable responses on large inputs
- **Seamless fallback**: Works even when Ollama is unavailable

### Beautiful Frontend
- **Clean, modern UI**: Minimalist design with professional aesthetics
- **Tab-based interface**: Switch between Router mode and Prompt Distillation mode
- **Real-time visualization**: See which model handled each query with model badges
- **Statistics dashboard**: Track LLM/SLM usage, costs, latency, and distribution
- **Message history**: Chat-like interface showing all queries and responses
- **Decision transparency**: See routing decisions with confidence scores and reasoning

### Performance & Analytics
- **Cost tracking**: Monitor estimated costs per query
- **Latency metrics**: Track average response times
- **Usage statistics**: See LLM vs SLM distribution percentages
- **Visual charts**: Model distribution visualization
- **Confidence scores**: Understand routing decision confidence

### Configuration & Customization
- **Flexible routing weights**: Adjust cost, latency, and quality weights
- **Customizable thresholds**: Configure complexity, token, and routing thresholds
- **Multiple providers**: Support for Ollama (local) and Gemini (cloud)
- **Model selection**: Easy switching between models via config

## 📦 Installation

### Backend

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## ⚙️ Setup

### Ollama (Local Models)

Install Ollama from [ollama.ai](https://ollama.ai) and pull the model:

```bash
ollama pull tinyllama
```

TinyLlama is only ~637MB. The system will automatically fallback to Gemini if Ollama is unavailable.

Make sure Ollama is running:
```bash
ollama serve
```

**Available Models:**
- `tinyllama` (~637MB) - Small, fast, current default
- `phi` (~1.6GB) - Better quality, slightly larger
- `gemma:2b` (~1.4GB) - Good balance of size and quality

### Gemini (Cloud API)

The API key is already configured in `config.yaml`. Gemini is used for:
- Automatic fallback when Ollama is unavailable
- Large input routing (2000+ tokens)
- High-complexity tasks
- Speed-optimized queries (1000+ tokens)

To use Gemini as primary LLM, change the `provider` in `config.yaml`:
```yaml
models:
  llm:
    provider: "gemini"
    model: "gemini-2.5-flash"
```

## 🚀 Usage

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

### Run CLI Examples

```bash
python example.py
```

## 🎯 Usage Modes

### Router Mode
- **Intelligent routing**: System automatically selects the best model
- **Priority selection**: Choose Cost, Balanced, or Speed optimization
- **Real-time decisions**: See routing decisions with explanations
- **Automatic fallback**: Handles errors gracefully

### Prompt Distillation Mode
- **Two-stage processing**: SLM refines your prompt, then LLM processes it
- **Optimized prompts**: Get better results with focused, refined prompts
- **Cost efficient**: Uses cheaper SLM for optimization step
- **Visual feedback**: See both refined prompt and final response

## 📊 API Endpoints

### POST `/query`
Process a query with intelligent routing.

**Request:**
```json
{
  "prompt": "Your question here",
  "priority": "balanced",
  "use_llm_fallback": true
}
```

**Response:**
```json
{
  "response": "Model response",
  "model_used": "llm",
  "decision": {
    "model_type": "llm",
    "confidence": 0.9,
    "reason": "High complexity task",
    "estimated_cost": 0.0001,
    "estimated_latency": 2.5
  },
  "fallback_used": false
}
```

### POST `/distill`
Distill prompt with SLM then process with LLM.

**Request:**
```json
{
  "prompt": "Your prompt here"
}
```

**Response:**
```json
{
  "response": "Final LLM response",
  "model_used": "gemini",
  "refined_prompt": "SLM-refined version",
  "original_prompt": "Your original prompt",
  "distillation_used": true
}
```

### GET `/health`
Health check endpoint.

## ⚙️ Configuration

Edit `config.yaml` to customize:

### Models
- **LLM**: Large model for complex tasks (default: Ollama TinyLlama)
- **SLM**: Small model for simple tasks (default: Ollama TinyLlama)
- **Gemini**: Cloud model for fallback and large inputs

### Routing Parameters
- `complexity_threshold`: Threshold for routing to LLM (default: 0.6)
- `max_slm_tokens`: Maximum tokens for SLM processing (default: 500)
- `large_input_threshold`: Auto-route to Gemini (default: 2000 tokens)
- `gemini_preferred_threshold`: Prefer Gemini for reliability (default: 1000 tokens)
- `fallback_enabled`: Enable automatic fallback (default: true)

### Optimization Weights
- `cost_weight`: Weight for cost optimization (default: 0.3)
- `latency_weight`: Weight for speed optimization (default: 0.3)
- `quality_weight`: Weight for quality optimization (default: 0.4)

### Priority Modes
- **Cost**: Minimize cost, prefer SLM when possible
- **Balanced**: Balance cost, speed, and quality
- **Speed**: Minimize latency, prefer faster models

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │ React + TypeScript UI
│   (Port 3k) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │ REST API Server
│  (Port 8k)  │
└──────┬──────┘
       │
       ├──► Router ───► Complexity Analysis
       │                Token Estimation
       │                Model Selection
       │
       ├──► Orchestrator ───► LLM Provider
       │                      SLM Provider
       │                      Gemini Provider
       │                      Fallback Logic
       │
       └──► Distiller ───► SLM Refinement
                           └──► LLM Processing
```

## 📁 Project Structure

```
llmslm/
├── api.py              # FastAPI server and endpoints
├── orchestrator.py     # Hybrid orchestration logic
├── router.py           # Intelligent routing engine
├── models.py           # LLM/SLM/Gemini providers
├── config.yaml         # Configuration file
├── main.py             # Server entry point
├── example.py          # CLI examples
├── requirements.txt    # Python dependencies
└── frontend/
    ├── src/
    │   ├── App.tsx            # Main app component
    │   ├── components/
    │   │   ├── ChatInterface.tsx      # Router mode UI
    │   │   ├── DistillInterface.tsx   # Distillation mode UI
    │   │   ├── Header.tsx             # App header
    │   │   ├── Tabs.tsx               # Mode switcher
    │   │   ├── MessageBubble.tsx      # Message display
    │   │   ├── ModelBadge.tsx         # Model indicator
    │   │   ├── InputArea.tsx          # Input component
    │   │   └── StatsPanel.tsx         # Statistics dashboard
    │   └── index.css
    └── package.json
```

## 🎨 Features in Detail

### Complexity Analysis Algorithm

The router analyzes prompts using a multi-factor scoring system to determine complexity (0-1 scale):

**Factors analyzed:**
1. **Word count** (max 0.3 points)
   - Score = `min(word_count / 100, 0.3)`
   - Example: 50 words = 0.15, 100+ words = 0.3

2. **Character count** (max 0.2 points)
   - Score = `min(char_count / 500, 0.2)`
   - Longer text indicates more complex input

3. **Question patterns** (max 0.2 points)
   - Score = `min(question_marks * 0.1, 0.2)`
   - Multiple questions indicate complexity

4. **Complex action verbs** (max 0.2 points)
   - Detects: analyze, explain, compare, evaluate, synthesize, create, design, develop
   - Score = `min(matches * 0.15, 0.2)`
   - These verbs indicate higher cognitive load

5. **Technical terminology** (max 0.1 points)
   - Detects: algorithm, architecture, optimization, implementation, framework, protocol
   - Score = `min(matches * 0.1, 0.1)`
   - Technical terms suggest specialized knowledge needed

**Final complexity score:** Sum of all factors, capped at 1.0

### Token Estimation

- **Formula:** `tokens = word_count * 1.3`
- Used for routing decisions and cost/latency estimation
- Large inputs (>2000 tokens) automatically routed to Gemini
- Medium-large inputs (>1000 tokens) prefer Gemini in speed mode

### Routing Decision Algorithm

The router follows a **priority-based decision tree**:

#### Step 1: Check for Very Large Inputs
```
IF estimated_tokens >= 2000 AND Gemini available:
    → Route to Gemini (confidence: 95%)
    Reason: "Very large input - routing to Gemini for speed and reliability"
```

#### Step 2: Priority-Specific Routing

**Cost Priority Mode:**
```
IF complexity < 0.8 AND word_count < max_slm_tokens:
    → Route to SLM (confidence: 80%)
    Reason: "Low complexity task, cost-optimized"
ELSE:
    → Continue to balanced routing
```

**Speed Priority Mode:**
```
IF estimated_tokens >= 1000 AND Gemini available:
    → Route to Gemini (confidence: 90%)
    Reason: "Large input - Gemini preferred for speed"
ELSE IF complexity < 0.7:
    → Route to SLM (confidence: 75%)
    Reason: "Simple task, speed-optimized"
ELSE:
    → Continue to balanced routing
```

#### Step 3: Complexity-Based Routing
```
IF complexity > threshold (0.6) OR word_count > max_slm_tokens:
    IF estimated_tokens >= 1000 AND Gemini available:
        → Route to Gemini (confidence: 90%)
        Reason: "High complexity and large input - Gemini preferred"
    ELSE:
        → Route to LLM (confidence: 90%)
        Reason: "High complexity or long input"
```

#### Step 4: Balanced Scoring (Default)

When no priority-specific rule applies, uses **weighted multi-factor scoring**:

**For each model (SLM, LLM, Gemini):**
1. **Cost Score** = `cost_weight * (1 - estimated_cost * 100)`
   - Lower cost = higher score
   - Normalized to prevent negative values

2. **Latency Score** = `latency_weight * (1 - estimated_latency / 10)`
   - Lower latency = higher score
   - Assumes max latency of 10 seconds

3. **Quality Score**:
   - **LLM:** `min(complexity * 1.2, 1.0)` - Better for complex tasks
   - **SLM:** `max(0.5, 1.0 - complexity * 0.5)` - Better for simple tasks
   - **Gemini:** `min(complexity * 1.3, 1.0)` - Best for complex tasks

**Final Score** = `cost_score + latency_score + quality_score`

**Model Selection:**
```
IF Gemini score > max(LLM score, SLM score) AND tokens >= 1000:
    → Route to Gemini
ELSE IF SLM score > LLM score AND complexity < 0.7:
    → Route to SLM
ELSE:
    → Route to LLM
```

### Latency Estimation

**SLM (Small Model):**
- Base latency: 0.5 seconds
- Token processing: `tokens / 500` seconds
- Formula: `0.5 + (tokens / 500)`

**LLM (Large Model):**
- Base latency: 2.0 seconds
- Token processing: `tokens / 100` seconds
- Formula: `2.0 + (tokens / 100)`

**Gemini (Cloud API):**
- Base latency: 1.0 seconds
- Token processing: `tokens / 200` seconds
- Formula: `1.0 + (tokens / 200)`

### Cost Estimation

- **Ollama models:** Free (cost_per_token = 0.0)
- **Gemini:** `tokens * cost_per_token` (default: 0.00001 per token)
- Total cost = `estimated_tokens * cost_per_token`

### Quality Check (Post-Processing)

After SLM response, checks quality:
1. **Minimum length:** Response must be ≥ 10 characters
2. **Proportional length:** Response must be ≥ 10% of prompt length
3. **Error indicators:** Counts occurrence of: "error", "cannot", "unable", "sorry", "i don't know"
   - If error count ≥ 2 → Triggers fallback to LLM

### Fallback Chain

**Automatic fallback hierarchy:**
1. **Primary model** (selected by router)
2. **Fallback to LLM** (if SLM fails or low quality)
3. **Fallback to Gemini** (if Ollama unavailable or connection error)
4. **Error reporting** (if all models fail)

**Fallback triggers:**
- Connection errors (Ollama not running)
- Low-quality responses (quality check fails)
- Timeout errors
- API errors

### Prompt Distillation Process

**Two-stage processing:**

1. **SLM Refinement Stage:**
   - Sends prompt to SLM with optimization instructions
   - SLM refines prompt to be more focused and clear
   - Instructions: Maintain intent, remove unnecessary details, clarify ambiguities, focus on key request

2. **LLM Processing Stage:**
   - Uses refined prompt (or original if refinement fails)
   - Sends to LLM (prefers Gemini if available)
   - Returns final response

**Fallback:**
- If SLM refinement fails → Uses original prompt
- If LLM fails and Gemini available → Uses Gemini
- Always returns both refined prompt and final response

## 📋 Routing Examples

### Example 1: Simple Question → SLM
**Prompt:** "What is the capital of France?"
- **Complexity:** ~0.1 (low word count, simple question)
- **Tokens:** ~8
- **Decision:** SLM (low complexity, cost-optimized)
- **Confidence:** 75%

### Example 2: Complex Technical Question → LLM/Gemini
**Prompt:** "Explain how quantum computing algorithms work and compare them to classical computing approaches, including performance implications and optimization strategies"
- **Complexity:** ~0.85 (high word count, technical terms, complex verbs)
- **Tokens:** ~30
- **Decision:** LLM or Gemini (high complexity, technical content)
- **Confidence:** 90%

### Example 3: Very Long Input → Gemini
**Prompt:** [2000+ word document]
- **Complexity:** Varies
- **Tokens:** ~2600
- **Decision:** Gemini (very large input, automatic routing)
- **Confidence:** 95%
- **Reason:** "Very large input - routing to Gemini for speed and reliability"

### Example 4: Speed Priority + Large Input → Gemini
**Prompt:** "Summarize this 1500-word article about machine learning..." (priority: speed)
- **Complexity:** Moderate
- **Tokens:** ~1950
- **Decision:** Gemini (speed priority + large input)
- **Confidence:** 90%

### Example 5: Cost Priority + Simple → SLM
**Prompt:** "Hello, how are you?" (priority: cost)
- **Complexity:** ~0.05
- **Tokens:** ~5
- **Decision:** SLM (cost-optimized, low complexity)
- **Confidence:** 80%

### Example 6: Balanced Mode → Weighted Scoring
**Prompt:** "Compare REST and GraphQL APIs" (priority: balanced)
- **Complexity:** ~0.55 (moderate)
- **Tokens:** ~8
- **Decision:** Based on weighted scores (cost, latency, quality)
- **Likely:** LLM (moderate complexity, quality-focused)
- **Confidence:** 85%

## 🔄 Complete Workflow

### Router Mode Workflow
```
User Input
    ↓
Complexity Analysis
    ↓
Token Estimation
    ↓
Priority Check
    ↓
Routing Decision (SLM/LLM/Gemini)
    ↓
Model Execution
    ↓
Quality Check (if SLM)
    ↓
Fallback (if needed)
    ↓
Response to User
```

### Distillation Mode Workflow
```
User Input
    ↓
SLM Refinement
    ↓
Refined Prompt Generated
    ↓
LLM Processing (with refined prompt)
    ↓
Final Response
    ↓
Display: Original → Refined → Response
```

## 🔧 Development

### Backend Development
```bash
# Run with auto-reload
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Testing
```bash
# Test API endpoints
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?", "priority": "balanced"}'
```

## 📝 License

MIT License - feel free to use and modify as needed.

## 🤝 Contributing

Contributions welcome! This is a learning project focused on LLM/SLM orchestration and routing.

