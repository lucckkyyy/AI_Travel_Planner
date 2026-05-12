# ✈️ AI Travel Planner
## 📘 Building a Full LLMOps Travel Planning Pipeline

I built this project to go beyond basic LLM applications and understand what a complete LLMOps pipeline looks like in practice. Most AI projects stop at "generate a response" — this one adds real-time search, output quality evaluation, and structured observability logging, making it a production-grade system rather than a demo.

The travel planner takes a destination, trip duration, and travel style, then runs a LangGraph agent that searches for current destination information, generates a detailed day-by-day itinerary, evaluates its own output quality using DeepEval, and logs every step to an ELK stack for observability.

---

## 🎯 Development Journey

### **Timeline & Approach**
- **Duration**: Built as part of a structured AI engineering portfolio series
- **Process**: Built each layer independently — agent first, then evaluation, then logging — before wiring them together
- **Focus**: LLMOps pipeline design, real-time search integration, LLM evaluation, and production observability

---

## 🧠 Skills I Developed Through This Project

### **LangGraph Agent Design**
- Building a stateful **LangGraph** workflow with typed state (TypedDict)
- Designing a two-node graph: search → plan → END
- Integrating **DuckDuckGo search** as a real-time tool for destination research
- Managing state flow between nodes and handling search failures gracefully

### **LLM Evaluation with DeepEval**
- Using **DeepEval** to measure itinerary quality programmatically
- Implementing `AnswerRelevancyMetric` to score how well the output matches the input
- Building a heuristic fallback scorer for environments where DeepEval isn't fully configured
- Understanding why LLM evaluation matters in production — you can't improve what you don't measure

### **ELK Stack Observability**
- Designing structured **JSON logging** using `python-json-logger`
- Writing logs to file for **Filebeat** pickup in production environments
- Sending logs directly to **Elasticsearch** when available for real-time indexing
- Visualizing pipeline metrics in **Kibana**
- Understanding the ELK stack architecture: app → Filebeat → Logstash → Elasticsearch → Kibana

### **LangGraph + Groq Integration**
- Connecting LangGraph nodes to **Groq's LPU** for ultra-fast itinerary generation
- Designing a detailed travel planner prompt with day/morning/evening structure
- Handling context window limits for DuckDuckGo search results
- Returning structured results from the graph for downstream evaluation and logging

### **FastAPI + Streamlit Full Stack**
- Building a `/plan` endpoint that orchestrates search → generate → evaluate → log
- Returning rich responses including itinerary, eval scores, and generation time
- Building a Streamlit dashboard with trip configuration, itinerary display, and log viewer
- Implementing a download button for saving itineraries as markdown files

### **GCP Cloud Run Deployment**
- Writing a **Cloud Run** YAML configuration for serverless deployment
- Building a GitHub Actions CI/CD pipeline that builds Docker images and deploys to GCP
- Using GCP Secret Manager references for API key injection
- Understanding Cloud Run's concurrency and timeout settings for LLM workloads

---

## ⚡ Technical Focus Areas

### **What I Built**
- LangGraph two-node agent: DuckDuckGo search → Groq itinerary generation
- DeepEval quality scorer with heuristic fallback
- Structured JSON ELK logger with Elasticsearch direct indexing
- FastAPI backend with plan, logs, and health endpoints
- Streamlit dashboard with itinerary viewer, eval scores, and log explorer
- ELK Docker Compose stack (Elasticsearch + Kibana)
- GCP Cloud Run deployment config with GitHub Actions CI/CD

### **Skills I Leveled Up**
- LLMOps pipeline design end-to-end
- LLM output evaluation with DeepEval metrics
- ELK stack for AI application observability
- LangGraph stateful agent design
- Real-time search tool integration
- GCP Cloud Run serverless deployment
- Structured JSON logging for production AI systems

---

## 🏗️ System Architecture

```
User Input (destination, days, style, budget)
      ↓
FastAPI /plan endpoint
      ↓
LangGraph Agent
  ├── [Node 1] DuckDuckGo Search
  │     → Real-time destination information
  └── [Node 2] Groq LLM Generation
        → Day-by-day itinerary
      ↓
DeepEval Quality Scoring
      ↓
ELK Logger
  ├── JSON file → Filebeat (production)
  └── Elasticsearch direct index
      ↓
Structured Response → Streamlit Dashboard

── GCP Deployment ──
Cloud Run → Docker container → GitHub Actions CI/CD
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent Framework | LangGraph |
| LLM | Groq — llama-3.1-8b-instant (free) |
| Search | DuckDuckGo (free, no API key) |
| Evaluation | DeepEval |
| Observability | ELK Stack (Elasticsearch + Kibana) |
| Backend | FastAPI |
| Frontend | Streamlit |
| Containerization | Docker + Docker Compose |
| Cloud | GCP Cloud Run |
| CI/CD | GitHub Actions |

---

## 🗂️ Project Structure

```
ai-travel-planner/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── agent/
│   │   └── travel_agent.py        # LangGraph agent + DuckDuckGo + Groq
│   ├── evaluation/
│   │   └── evaluator.py           # DeepEval quality scoring
│   ├── logging_elk/
│   │   └── elk_logger.py          # Structured JSON + Elasticsearch logger
│   └── requirements.txt
├── frontend/
│   └── app.py                     # Streamlit dashboard
├── elk/
│   └── docker-compose.yml         # Elasticsearch + Kibana stack
├── gcp/
│   └── cloud-run.yaml             # GCP Cloud Run deployment config
├── .github/workflows/
│   └── ci-cd.yml                  # GitHub Actions → GCP deployment
├── docker-compose.yml
└── .env.example
```

---

## 🚀 The Learning Outcome

This project taught me that production AI systems need three things beyond just a working LLM call: evaluation (how good is the output?), observability (what happened during generation?), and deployment (how does it run in the real world?).

Building the DeepEval integration made me think carefully about what "good" means for an AI-generated itinerary — relevancy, completeness, coherence. The ELK logging taught me how to instrument an AI pipeline so that every request is traceable. And the GCP Cloud Run config showed me how to take a local Docker container to a globally accessible serverless endpoint.

---

*Author: Aryan Rajguru*
