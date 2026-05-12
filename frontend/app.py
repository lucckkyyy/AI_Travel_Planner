"""
Streamlit Frontend — AI Travel Planner
Beautiful interface for generating and viewing AI travel itineraries.
"""
import streamlit as st
import httpx

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ AI Travel Planner")
st.markdown("*Powered by LangGraph + Groq + DuckDuckGo — real-time personalized itineraries*")
st.divider()


def api_get(path):
    try:
        r = httpx.get(f"{API_BASE}{path}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_post(path, data):
    try:
        r = httpx.post(f"{API_BASE}{path}", json=data, timeout=90)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🗺️ Plan Your Trip")

destination = st.sidebar.text_input(
    "Destination",
    placeholder="e.g. Tokyo, Japan",
    value="Tokyo, Japan",
)

days = st.sidebar.slider("Number of Days", min_value=1, max_value=14, value=5)

travel_style = st.sidebar.selectbox(
    "Travel Style",
    [
        "cultural and historical",
        "foodie and culinary",
        "adventure and outdoor",
        "luxury and relaxation",
        "budget backpacker",
        "family friendly",
        "romantic couples",
        "photography and sightseeing",
    ],
)

budget = st.sidebar.selectbox(
    "Budget Level",
    ["budget", "moderate", "luxury"],
    index=1,
)

st.sidebar.divider()
st.sidebar.markdown("### 🤖 Pipeline")
st.sidebar.markdown("""
1. **Search** — DuckDuckGo fetches current destination info
2. **Plan** — Groq LLM generates day-by-day itinerary
3. **Evaluate** — DeepEval scores the output quality
4. **Log** — ELK stack logs the full request pipeline
""")

generate_btn = st.sidebar.button("🚀 Generate Itinerary", type="primary", use_container_width=True)

# ── Main Area ─────────────────────────────────────────────────────────────────
page = st.radio("View", ["📋 Itinerary", "📊 Logs"], horizontal=True)

if page == "📋 Itinerary":
    if generate_btn:
        if not destination:
            st.error("Please enter a destination!")
        else:
            with st.spinner(f"🔍 Searching + ✈️ Planning your {days}-day trip to {destination}... (30-60s)"):
                result = api_post("/plan", {
                    "destination":   destination,
                    "days":          days,
                    "travel_style":  travel_style,
                    "budget":        budget,
                })

            if result:
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("📍 Destination", result["destination"])
                col2.metric("📅 Days", result["days"])
                col3.metric("⚡ Generation Time", f"{result['generation_time_ms']}ms")

                eval_scores = result.get("eval_scores", {})
                score = eval_scores.get("relevancy_score", 0)
                col4.metric("🎯 Quality Score", f"{score:.1%}")

                st.divider()

                # Eval details
                with st.expander("📊 DeepEval Quality Report"):
                    method = eval_scores.get("evaluation_method", "unknown")
                    st.markdown(f"**Evaluation Method:** `{method}`")
                    st.markdown(f"**Relevancy Score:** `{score:.3f}`")
                    if "check_details" in eval_scores:
                        st.json(eval_scores["check_details"])

                # Itinerary
                st.markdown("---")
                st.markdown(result["itinerary"])

                # Download button
                st.download_button(
                    "📥 Download Itinerary",
                    data=result["itinerary"],
                    file_name=f"{destination.replace(', ', '_')}_{days}days.md",
                    mime="text/markdown",
                )
    else:
        st.info("👈 Fill in your trip details in the sidebar and click **Generate Itinerary**!")

        st.markdown("### 🌍 Popular Destinations to Try")
        cols = st.columns(4)
        suggestions = ["Tokyo, Japan", "Paris, France", "Bali, Indonesia", "New York, USA"]
        for col, sug in zip(cols, suggestions):
            col.markdown(f"**{sug}**")

elif page == "📊 Logs":
    st.header("📊 ELK Pipeline Logs")
    st.markdown("*Structured JSON logs — in production these flow into Elasticsearch → Kibana*")

    logs_data = api_get("/logs?lines=20")
    if logs_data and logs_data["count"] > 0:
        st.metric("Total Log Entries", logs_data["count"])
        for log in reversed(logs_data["logs"]):
            event = log.get("event", "unknown")
            icon = {"itinerary_request": "📨", "itinerary_generated": "✅", "error": "❌"}.get(event, "📝")
            with st.expander(f"{icon} {event} — {log.get('timestamp', '')[:19]}"):
                st.json(log)
    else:
        st.info("No logs yet — generate an itinerary first!")
