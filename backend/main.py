"""
FastAPI Backend — AI Travel Planner

Endpoints:
  POST /plan         — Generate a full travel itinerary
  GET  /logs         — Retrieve recent log entries
  GET  /health       — Health check
"""
import uuid
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent.travel_agent import generate_itinerary
from evaluation.evaluator import evaluate_itinerary
from logging_elk.elk_logger import (
    log_itinerary_request,
    log_itinerary_generated,
    log_error,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AI Travel Planner starting up...")
    logger.info("✅ Ready!")
    yield


app = FastAPI(
    title="AI Travel Planner API",
    description="LangGraph travel agent with DuckDuckGo search, Groq LLM, DeepEval, and ELK logging.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    destination: str = Field(..., example="Tokyo, Japan")
    days: int = Field(..., ge=1, le=14, example=5)
    travel_style: str = Field(..., example="cultural and foodie")
    budget: str = Field(default="moderate", example="moderate")


class PlanResponse(BaseModel):
    request_id: str
    destination: str
    days: int
    itinerary: str
    eval_scores: dict
    generation_time_ms: float


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-travel-planner"}


@app.post("/plan", response_model=PlanResponse)
async def plan_trip(req: PlanRequest):
    """
    Generate a complete travel itinerary.
    Pipeline: DuckDuckGo search → Groq LLM → DeepEval scoring → ELK logging
    """
    request_id = str(uuid.uuid4())[:8]

    # Log the request
    log_itinerary_request(
        destination=req.destination,
        days=req.days,
        travel_style=req.travel_style,
        request_id=request_id,
    )

    try:
        start_time = time.time()

        # Run the LangGraph agent
        result = generate_itinerary(
            destination=req.destination,
            days=req.days,
            travel_style=req.travel_style,
            budget=req.budget,
        )

        generation_time_ms = round((time.time() - start_time) * 1000, 2)

        # Evaluate with DeepEval
        eval_scores = evaluate_itinerary(
            destination=req.destination,
            days=req.days,
            travel_style=req.travel_style,
            itinerary=result["itinerary"],
        )

        # Log completion to ELK
        log_itinerary_generated(
            request_id=request_id,
            destination=req.destination,
            generation_time_ms=generation_time_ms,
            eval_scores=eval_scores,
        )

        return PlanResponse(
            request_id=request_id,
            destination=req.destination,
            days=req.days,
            itinerary=result["itinerary"],
            eval_scores=eval_scores,
            generation_time_ms=generation_time_ms,
        )

    except Exception as e:
        log_error(request_id, str(e))
        logger.error(f"Planning error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs")
async def get_logs(lines: int = 50):
    """Return recent log entries from the JSON log file."""
    try:
        import json
        logs = []
        with open("logs/travel-planner.json", "r") as f:
            for line in f.readlines()[-lines:]:
                try:
                    logs.append(json.loads(line))
                except Exception:
                    pass
        return {"logs": logs, "count": len(logs)}
    except FileNotFoundError:
        return {"logs": [], "count": 0}
