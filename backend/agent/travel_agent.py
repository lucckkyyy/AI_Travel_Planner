"""
Travel Agent — LangGraph agent that:
1. Searches for real information about the destination (DuckDuckGo)
2. Generates a structured day-by-day itinerary (Groq LLM)
3. Returns a complete travel plan

Graph:
  search_destination → plan_itinerary → END
"""
import os
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from dotenv import load_dotenv

load_dotenv()


# ── State ─────────────────────────────────────────────────────────────────────
class TravelState(TypedDict):
    destination: str
    days: int
    travel_style: str
    budget: str
    search_results: Optional[str]
    itinerary: Optional[str]


# ── LLM ───────────────────────────────────────────────────────────────────────
def get_llm():
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
    )


# ── Node 1: Search ────────────────────────────────────────────────────────────
def search_node(state: TravelState) -> dict:
    """Search for current info about the destination."""
    print(f"🔍 Searching for info about {state['destination']}...")

    search = DuckDuckGoSearchRun()
    try:
        results = search.run(
            f"{state['destination']} travel guide top attractions {state['days']} days"
        )
        # Limit results to avoid token overflow
        search_results = results[:2000] if len(results) > 2000 else results
    except Exception as e:
        search_results = f"Search unavailable: {e}. Using general knowledge."

    print(f"  ✅ Search complete ({len(search_results)} chars)")
    return {"search_results": search_results}


# ── Node 2: Plan Itinerary ────────────────────────────────────────────────────
ITINERARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert travel planner with deep knowledge of destinations worldwide.
Create detailed, realistic, and engaging travel itineraries.

Guidelines:
- Structure each day with Morning, Afternoon, and Evening sections
- Include specific restaurant recommendations with cuisine type
- Suggest accommodation options matching the travel style and budget
- Add practical tips (best time to visit, transport between locations, booking advice)
- Include estimated costs where relevant
- Make it feel personal and exciting, not like a generic tourist guide
- Consider the travel style: budget travelers want cheap eats and hostels; luxury travelers want fine dining and 5-star hotels"""),

    ("human", """Create a detailed {days}-day itinerary for {destination}.

Travel Style: {travel_style}
Budget Level: {budget}

Recent information about the destination:
{search_results}

Please create a complete day-by-day itinerary with specific places, restaurants, and tips.
Format each day clearly as "## Day X: [Theme]" with Morning/Afternoon/Evening sections."""),
])


def plan_itinerary_node(state: TravelState) -> dict:
    """Generate the full itinerary using Groq LLM."""
    print(f"🤖 Generating {state['days']}-day itinerary for {state['destination']}...")

    llm = get_llm()
    chain = ITINERARY_PROMPT | llm | StrOutputParser()

    itinerary = chain.invoke({
        "destination":   state["destination"],
        "days":          state["days"],
        "travel_style":  state["travel_style"],
        "budget":        state["budget"],
        "search_results": state.get("search_results", "No search results available."),
    })

    print(f"  ✅ Itinerary generated ({len(itinerary)} chars)")
    return {"itinerary": itinerary}


# ── Build Graph ───────────────────────────────────────────────────────────────
def build_travel_graph():
    workflow = StateGraph(TravelState)

    workflow.add_node("search",  search_node)
    workflow.add_node("plan",    plan_itinerary_node)

    workflow.set_entry_point("search")
    workflow.add_edge("search", "plan")
    workflow.add_edge("plan",   END)

    return workflow.compile()


_graph = None

def get_graph():
    global _graph
    if _graph is None:
        _graph = build_travel_graph()
    return _graph


def generate_itinerary(
    destination: str,
    days: int,
    travel_style: str,
    budget: str,
) -> dict:
    """
    Run the full travel planning pipeline.
    Returns itinerary text and search results used.
    """
    graph = get_graph()

    initial_state: TravelState = {
        "destination":   destination,
        "days":          days,
        "travel_style":  travel_style,
        "budget":        budget,
        "search_results": None,
        "itinerary":     None,
    }

    print(f"\n{'='*60}")
    print(f"✈️  Planning trip to {destination} ({days} days, {travel_style})")
    print(f"{'='*60}")

    final_state = graph.invoke(initial_state)

    print(f"{'='*60}")
    print(f"✅ Itinerary complete!")
    print(f"{'='*60}\n")

    return {
        "itinerary":     final_state["itinerary"],
        "search_results": final_state["search_results"],
    }
