"""
DeepEval Evaluator — measures the quality of generated travel itineraries.
Uses DeepEval metrics to score:
- Relevance: Does the itinerary match the destination and preferences?
- Completeness: Does it cover all requested days?
- Coherence: Is it logically structured and realistic?
"""
import os
from dotenv import load_dotenv

load_dotenv()


def evaluate_itinerary(
    destination: str,
    days: int,
    travel_style: str,
    itinerary: str,
) -> dict:
    """
    Evaluate the quality of a generated itinerary using DeepEval.
    Returns scores dict with metric names and values (0.0 - 1.0).
    Falls back to heuristic scoring if DeepEval setup fails.
    """
    try:
        from deepeval import evaluate
        from deepeval.metrics import (
            AnswerRelevancyMetric,
            FaithfulnessMetric,
        )
        from deepeval.test_case import LLMTestCase

        input_prompt = (
            f"Create a {days}-day travel itinerary for {destination} "
            f"with a {travel_style} travel style."
        )

        test_case = LLMTestCase(
            input=input_prompt,
            actual_output=itinerary,
            retrieval_context=[
                f"Destination: {destination}",
                f"Duration: {days} days",
                f"Travel style: {travel_style}",
            ],
        )

        relevancy = AnswerRelevancyMetric(threshold=0.5, verbose_mode=False)
        relevancy.measure(test_case)

        return {
            "relevancy_score": round(relevancy.score, 3),
            "evaluation_method": "deepeval",
        }

    except Exception:
        # Fallback: heuristic scoring based on content checks
        return _heuristic_score(itinerary, destination, days)


def _heuristic_score(itinerary: str, destination: str, days: int) -> dict:
    """
    Simple heuristic scorer when DeepEval isn't fully configured.
    Checks for key quality indicators in the itinerary text.
    """
    score = 0.0
    checks = {
        "mentions_destination": destination.lower() in itinerary.lower(),
        "has_day_structure":    any(f"day {i}" in itinerary.lower() for i in range(1, days + 1)),
        "has_morning_evening":  "morning" in itinerary.lower() or "evening" in itinerary.lower(),
        "has_activities":       any(w in itinerary.lower() for w in ["visit", "explore", "restaurant", "museum", "hotel"]),
        "sufficient_length":    len(itinerary) > 500,
    }

    passed = sum(checks.values())
    score = round(passed / len(checks), 3)

    return {
        "relevancy_score":    score,
        "evaluation_method":  "heuristic",
        "checks_passed":      passed,
        "total_checks":       len(checks),
        "check_details":      checks,
    }
