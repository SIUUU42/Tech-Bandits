"""
Flight Disruption Recovery Assistant - Streamlit UI

Fast, intelligent Streamlit chat app for finding alternative flights during cancellations.
"""

import streamlit as st
import sqlite3
from datetime import datetime
from typing import List, Dict, Tuple
import logging

from database import setup_database, get_all_flights
from agent import FlightDisruptionAgent
from utils import format_flight_display, risk_label, calculate_weather_score

# Configure page
st.set_page_config(
    page_title="✈️ Flight Recovery Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
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


@st.cache_resource
def initialize_app():
    """Initialize database and agent (cached for performance)."""
    setup_database()
    agent = FlightDisruptionAgent()
    return agent


@st.cache_data
def load_flight_count():
    """Cache flight count for stats."""
    try:
        conn = sqlite3.connect("flights.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM flights")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0


def render_chat_message(role: str, content: str, is_response: bool = False):
    """Render a chat message."""
    with st.chat_message(role, avatar="👤" if role == "user" else "🤖"):
        if is_response:
            st.markdown(content)
        else:
            st.write(content)


def render_flight_with_explanation(flight: Dict, explanation: str, flight_id: str):
    """Render flight card with 'Why this flight?' button."""
    with st.container(border=True):
        # Flight info
        st.markdown(format_flight_display(flight))
        
        # Why this flight button
        col1, col2 = st.columns([0.3, 0.7])
        with col1:
            if st.button(
                "💡 Why this flight?",
                key=f"why_{flight_id}",
                use_container_width=True
            ):
                st.session_state.why_expanded[flight_id] = not st.session_state.why_expanded.get(flight_id, False)
        
        # Show explanation if expanded
        if st.session_state.why_expanded.get(flight_id, False):
            with col2:
                st.info(explanation)


def render_disruption_mode():
    """Render the disruption mode input section."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚨 DISRUPTION MODE")
    st.sidebar.markdown("*Direct flight ID entry for quick recovery*")
    
    disruption_flight_id = st.sidebar.text_input(
        "Enter flight ID (e.g., AI203)",
        placeholder="AI203",
        key="disruption_input"
    )
    
    if st.sidebar.button("🔍 Find Alternatives", use_container_width=True):
        if disruption_flight_id.strip():
            st.session_state.disruption_query = disruption_flight_id.strip()
            st.rerun()
        else:
            st.sidebar.error("Please enter a flight ID")


def process_user_input(user_input: str):
    """Process user input through agent."""
    if not user_input.strip():
        return
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get agent response
    try:
        agent = st.session_state.agent
        response, ranked_flights = agent.run(user_input)
        
        # Store ranked flights and explanations for later rendering
        st.session_state.last_ranked_flights = ranked_flights
        if hasattr(agent.ranking_engine, '__dict__'):
            explanations = {}
            for flight, score in ranked_flights:
                explanations[flight["flight_id"]] = agent.ranking_engine.generate_explanation(flight, score)
            st.session_state.explanations = explanations
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
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
    flight_count = load_flight_count()
    
    # Header
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.title("✈️ Flight Disruption Recovery Assistant")
        st.markdown("*Your AI-powered solution for flight cancellations and delays*")
    
    with col2:
        st.metric("Flights Available", flight_count)
    
    # Sidebar info
    with st.sidebar:
        st.markdown("### 📌 How to use")
        st.markdown("""
        1. **Chat Mode:** Ask natural questions
           - "Show flights from Delhi to Pune"
           - "Flights tomorrow afternoon"
        
        2. **Recovery Mode:** Enter cancelled flight ID
           - Use disruption input below
           - Get best alternatives instantly
        
        3. **Why this flight?**
           - Click button on any flight
           - See scoring breakdown
        """)
        
        st.markdown("---")
        st.markdown("### 🎯 Example Queries")
        st.markdown("""
        - "Flights from Mumbai to Bangalore tomorrow"
        - "Show afternoon flights Delhi to Hyderabad"
        - "Find alternatives for AI203"
        - Direct flight ID: AI203
        """)
    
    # Render disruption mode
    render_disruption_mode()
    
    # Render chat history
    st.markdown("---")
    
    for message in st.session_state.messages:
        render_chat_message(
            role=message["role"],
            content=message["content"],
            is_response=(message["role"] == "assistant")
        )
        
        # Render flights if present
        if message.get("flights"):
            for flight, score in message["flights"]:
                explanation = st.session_state.explanations.get(
                    flight["flight_id"],
                    "Selected as one of the best available options."
                )
                render_flight_with_explanation(
                    flight,
                    explanation,
                    flight["flight_id"]
                )
    
    # Chat input
    st.markdown("---")
    
    # Check if disruption mode was triggered
    if "disruption_query" in st.session_state:
        user_input = st.session_state.disruption_query
        del st.session_state.disruption_query
        process_user_input(user_input)
        st.rerun()
    else:
        # Normal chat input
        user_input = st.chat_input(
            "Ask about flights... (e.g., 'Show flights from Delhi to Pune tomorrow afternoon')",
            key="chat_input"
        )
        
        if user_input:
            process_user_input(user_input)
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.85em;'>
    ✨ Flight Disruption Recovery Assistant | Built for Hackathon | Powered by LangGraph & Streamlit
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
