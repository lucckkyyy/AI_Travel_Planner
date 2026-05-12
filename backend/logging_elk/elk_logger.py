"""
ELK Logger — structured JSON logging for the ELK stack.
Logs are written as JSON to both console and file.
In production, Filebeat picks up the log file and ships to Elasticsearch.
If Elasticsearch is running locally, logs are also indexed directly.
"""
import os
import json
import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ES_INDEX = os.getenv("ELASTICSEARCH_INDEX", "travel-planner-logs")

# ── JSON Logger Setup ─────────────────────────────────────────────────────────
logger = logging.getLogger("travel-planner")
logger.setLevel(getattr(logging, LOG_LEVEL))

# Console handler with JSON formatting
console_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler — Filebeat picks this up in production
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/travel-planner.json")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def _send_to_elasticsearch(doc: dict) -> None:
    """Try to send log to Elasticsearch. Silently skip if not running."""
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch(ES_URL, request_timeout=2)
        if es.ping():
            es.index(index=ES_INDEX, document=doc)
    except Exception:
        pass  # ES not running — that's fine, file logs still work


def log_itinerary_request(
    destination: str,
    days: int,
    travel_style: str,
    request_id: str,
) -> None:
    doc = {
        "event":        "itinerary_request",
        "destination":  destination,
        "days":         days,
        "travel_style": travel_style,
        "request_id":   request_id,
        "timestamp":    datetime.utcnow().isoformat(),
    }
    logger.info("Itinerary requested", extra=doc)
    _send_to_elasticsearch(doc)


def log_itinerary_generated(
    request_id: str,
    destination: str,
    generation_time_ms: float,
    eval_scores: dict,
) -> None:
    doc = {
        "event":              "itinerary_generated",
        "request_id":         request_id,
        "destination":        destination,
        "generation_time_ms": generation_time_ms,
        "eval_scores":        eval_scores,
        "timestamp":          datetime.utcnow().isoformat(),
    }
    logger.info("Itinerary generated", extra=doc)
    _send_to_elasticsearch(doc)


def log_error(request_id: str, error: str) -> None:
    doc = {
        "event":      "error",
        "request_id": request_id,
        "error":      error,
        "timestamp":  datetime.utcnow().isoformat(),
    }
    logger.error("Error occurred", extra=doc)
    _send_to_elasticsearch(doc)
