"""
Flight Disruption Recovery Assistant - Streamlit UI

Fast, intelligent Streamlit chat app for finding alternative flights during cancellations.
"""

import streamlit as st
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Tuple
import logging

from database import setup_database, get_all_flights, sync_live_planes_to_db
from agent import FlightDisruptionAgent
from utils import format_flight_display, risk_label, calculate_weather_score
from translator_utils import get_text, LANGUAGES, translate_text
from custom_css import inject_css

# Compatibility for different Streamlit versions
def rerun():
    """Trigger app rerun - compatible with different Streamlit versions."""
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# Configure page
st.set_page_config(
    page_title="✈️ Flight Recovery Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS for professional styling
inject_css()

# Add GitHub button next to Deploy button in top-right corner
st.markdown(
    """
    <style>
    .github-button {
        position: fixed;
        top: 0.75rem;
        right: 7rem;
        z-index: 999999;
    }
    .github-button a {
        text-decoration: none;
    }
    .github-button button {
        background: linear-gradient(135deg, #24292e 0%, #1a1e22 100%);
        color: white;
        border: none;
        border-radius: 0.25rem;
        padding: 0.3rem 0.75rem;
        font-weight: 500;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.875rem;
        height: 2.25rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .github-button button:hover {
        background: linear-gradient(135deg, #2d3339 0%, #24292e 100%);
        box-shadow: 0 2px 6px rgba(0,0,0,0.18);
        transform: translateY(-1px);
    }
    </style>
    <div class="github-button">
        <a href="https://github.com/SIUUU42/Tech-Bandits" target="_blank">
            <button>
                <svg height="16" width="16" viewBox="0 0 16 16" fill="white">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                </svg>
                GitHub
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None

if "last_ranked_flights" not in st.session_state:
    st.session_state.last_ranked_flights = []

if "explanations" not in st.session_state:
    st.session_state.explanations = {}

if "why_expanded" not in st.session_state:
    st.session_state.why_expanded = {}

if "data_source_filter" not in st.session_state:
    st.session_state.data_source_filter = "All"

if "language" not in st.session_state:
    st.session_state.language = "English"


@st.cache_resource
def initialize_app():
    """Initialize database and agent (cached for performance)."""
    setup_database()
    agent = FlightDisruptionAgent()
    return agent


@st.cache_data
def load_flight_count(db_mtime: float, data_source_filter: str = "All"):
    """Cache flight count for stats."""
    try:
        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        
        # Filter by data source
        if data_source_filter == "Live Only":
            cursor.execute("SELECT COUNT(*) FROM flights WHERE data_source='opensky'")
        elif data_source_filter == "Fake Only":
            cursor.execute("SELECT COUNT(*) FROM flights WHERE data_source='fake'")
        else:  # All
            cursor.execute("SELECT COUNT(*) FROM flights")
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0


def _looks_like_flight_list(content: str) -> bool:
    """Detect old duplicated flight lists in assistant messages."""
    if not content:
        return False
    markers = ["✈️", "Seats:", "Weather Risk:", "Delay Risk:", "Price:"]
    return any(marker in content for marker in markers)


def render_chat_message(role: str, content: str, is_response: bool = False):
    """Render a chat message."""
    with st.chat_message(role, avatar="👤" if role == "user" else "🤖"):
        if is_response:
            st.markdown(content)
        else:
            st.write(content)


def render_flight_with_explanation(flight: Dict, explanation: str, flight_id: str, unique_id: str = None):
    """Render flight card with 'Why this flight?' button.
    
    Args:
        flight: Flight data dict
        explanation: Ranking explanation text
        flight_id: Flight identifier
        unique_id: Unique identifier for this render (to avoid duplicate keys across messages)
    """
    if unique_id is None:
        unique_id = flight_id
    
    with st.container():
        # Flight info
        lang_code = LANGUAGES.get(st.session_state.language, "en")
        st.markdown(format_flight_display(flight, lang_code=lang_code))
        
        # Why this flight button with unique key
        col1, col2 = st.columns([0.3, 0.7])
        with col1:
            if st.button(
                get_text("💡 Why this flight?", lang_code),
                key=f"why_{unique_id}",
                use_container_width=True
            ):
                st.session_state.why_expanded[unique_id] = not st.session_state.why_expanded.get(unique_id, False)
        
        # Show explanation if expanded
        if st.session_state.why_expanded.get(unique_id, False):
            with col2:
                # Translate explanation if needed
                lang_code = LANGUAGES.get(st.session_state.language, "en")
                translated_explanation = get_text(explanation, lang_code)
                st.info(translated_explanation)


def render_disruption_mode():
    """Render the disruption mode input section."""
    lang_code = LANGUAGES.get(st.session_state.language, "en")
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 🚨 {get_text('DISRUPTION MODE', lang_code)}")
    st.sidebar.markdown(f"*{get_text('Direct flight ID entry for quick recovery', lang_code)}*")
    
    disruption_flight_id = st.sidebar.text_input(
        get_text("Enter flight ID", lang_code),
        placeholder="AI203",
        key="disruption_input"
    )
    
    if st.sidebar.button(get_text("Find Alternatives", lang_code), use_container_width=True):
        if disruption_flight_id.strip():
            st.session_state.disruption_query = disruption_flight_id.strip()
            rerun()
        else:
            st.sidebar.error(get_text("Please enter a flight ID", lang_code))


def render_live_data_section():
    """Render the live data sync and filtering section."""
    lang_code = LANGUAGES.get(st.session_state.language, "en")
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 🛰️ {get_text('LIVE DATA', lang_code)}")
    st.sidebar.markdown(f"*{get_text('Real-time aircraft from OpenSky Network', lang_code)}*")
    
    if st.sidebar.button(get_text("Sync Live Planes (OpenSky)", lang_code), use_container_width=True, key="sync_opensky"):
        with st.spinner(get_text("Fetching live aircraft from OpenSky Network...", lang_code)):
            try:
                stats = sync_live_planes_to_db()
                
                if stats.get("errors") and stats["errors"] > 0:
                    error_msg = stats.get("error_msg", "Unknown error")
                    st.sidebar.error(f"⚠️ {get_text('Sync had errors', lang_code)}: {error_msg}")
                else:
                    st.sidebar.success(
                        f"✅ {get_text('Synced', lang_code)} {stats.get('live_planes', 0)} {get_text('aircraft', lang_code)} → "
                        f"{stats.get('materialized_flights', 0)} {get_text('flights', lang_code)}"
                    )
                    # Force rerun to refresh flight data
                    rerun()
            except Exception as e:
                st.sidebar.error(f"❌ {get_text('Sync failed', lang_code)}: {str(e)}")
    
    # Data source filter
    options = ["All", "Live Only", "Fake Only"]
    translated_options = [get_text(opt, lang_code) for opt in options]
    
    selected_translated = st.sidebar.selectbox(
        get_text("Data Source Filter", lang_code),
        translated_options,
        key="data_source_selectbox_ui",
        index=options.index(st.session_state.data_source_filter)
    )
    
    # Map back to original option
    st.session_state.data_source_filter = options[translated_options.index(selected_translated)]


def process_user_input(user_input: str):
    """Process user input through agent."""
    if not user_input.strip():
        return
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Convert UI data source filter to database value
    filter_map = {
        "All": None,
        "Live Only": "opensky",
        "Fake Only": "fake"
    }
    data_source = filter_map.get(st.session_state.data_source_filter, None)
    
    # Get agent response
    try:
        agent = st.session_state.agent
        response, ranked_flights = agent.run(user_input, data_source=data_source)
        
        # Store ranked flights and explanations for later rendering
        st.session_state.last_ranked_flights = ranked_flights
        if hasattr(agent.ranking_engine, '__dict__'):
            explanations = {}
            for flight, score in ranked_flights:
                explanations[flight["flight_id"]] = agent.ranking_engine.generate_explanation(flight, score)
            st.session_state.explanations = explanations
        
        # Add assistant response to chat history
        lang_code = LANGUAGES.get(st.session_state.language, "en")
        translated_response = get_text(response, lang_code)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": translated_response,
            "flights": ranked_flights
        })
    
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        error_msg = f"❌ Error: {str(e)}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_msg,
            "flights": []
        })


def main():
    """Main Streamlit app."""
    
    # Initialize
    st.session_state.agent = initialize_app()
    db_mtime = os.path.getmtime("flights.db") if os.path.exists("flights.db") else 0
    flight_count = load_flight_count(db_mtime, st.session_state.data_source_filter)
    
    lang_code = LANGUAGES.get(st.session_state.language, "en")

    # Header
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.title(f"✈️ {get_text('Flight Disruption Recovery Assistant', lang_code)}")
        st.markdown(f"*{get_text('Your AI-powered solution for flight cancellations and delays', lang_code)}*")
    
    with col2:
        st.metric(get_text("Flights Available", lang_code), flight_count)
    
    # Sidebar info
    with st.sidebar:
        st.session_state.language = st.selectbox(
            "🌐 Select Language",
            options=list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(st.session_state.language)
        )
        
        st.markdown(f"### 📌 {get_text('How to use', lang_code)}")
        st.markdown(f"""
        1. **{get_text('Chat Mode', lang_code)}:** {get_text('Ask natural questions', lang_code)}
           - "Show flights from Delhi to Pune"
           - "Flights tomorrow afternoon"
        
        2. **{get_text('Recovery Mode', lang_code)}:** {get_text('Enter cancelled flight ID', lang_code)}
           - {get_text('Use disruption input below', lang_code)}
           - {get_text('Get best alternatives instantly', lang_code)}
        
        3. **{get_text('Why this flight?', lang_code)}**
           - {get_text('Click button on any flight', lang_code)}
           - {get_text('See scoring breakdown', lang_code)}
        """)
        
        st.markdown("---")
        st.markdown(f"### 🎯 {get_text('Example Queries', lang_code)}")
        st.markdown("""
        - "Flights from Mumbai to Bangalore tomorrow"
        - "Show afternoon flights Delhi to Hyderabad"
        - "Find alternatives for AI203"
        - Direct flight ID: AI203
        """)
    
    # Render disruption mode
    render_disruption_mode()
    
    # Render live data section
    render_live_data_section()
    
    # Render chat history
    st.markdown("---")
    
    for msg_idx, message in enumerate(st.session_state.messages):
        if message["role"] == "assistant" and message.get("flights"):
            if not _looks_like_flight_list(message.get("content", "")):
                render_chat_message(
                    role=message["role"],
                    content=message["content"],
                    is_response=True
                )
        else:
            render_chat_message(
                role=message["role"],
                content=message["content"],
                is_response=(message["role"] == "assistant")
            )
        
        # Render flights if present
        if message.get("flights"):
            for flight_idx, (flight, score) in enumerate(message["flights"]):
                explanation = st.session_state.explanations.get(
                    flight["flight_id"],
                    "Selected as one of the best available options."
                )
                # Create unique ID combining message and flight index
                unique_id = f"msg{msg_idx}_flight{flight_idx}_{flight['flight_id']}"
                render_flight_with_explanation(
                    flight,
                    explanation,
                    flight["flight_id"],
                    unique_id=unique_id
                )
    
    # Chat input
    st.markdown("---")
    
    # Check if disruption mode was triggered
    if "disruption_query" in st.session_state:
        user_input = st.session_state.disruption_query
        del st.session_state.disruption_query
        process_user_input(user_input)
        rerun()
    else:
        # Normal chat input
        user_input = st.chat_input(
            get_text("Ask about flights...", lang_code),
            key="chat_input"
        )
        
        if user_input:
            process_user_input(user_input)
            rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.85em;'>
    ✨ Flight Disruption Recovery Assistant | Built for Hackathon | Powered by LangGraph & Streamlit
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
