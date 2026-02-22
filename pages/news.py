"""
Streamlit page for Disruption News with Twitter & RSS integration.

Displays flight disruption news from RSS feeds and Twitter with search functionality.
"""

import streamlit as st
import requests
from datetime import datetime
import logging

from twitter_utils import (
    TwitterSearchBuilder,
    infer_airlines_from_query,
    detect_disruption_keywords,
    detect_news_request
)
from custom_css import inject_css

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inject custom CSS
inject_css()

# ============================================
# PAGE CONFIGURATION
# ============================================

# Page config
st.set_page_config(
    page_title="📰 Disruption News",
    page_icon="📰",
    layout="wide"
)

# ============================================
# PAGE TITLE
# ============================================

st.markdown("""
# 📰 Disruption & Flight News
*Stay updated on flight disruptions, cancellations, and aviation news*
""")

st.markdown("---")

# ============================================
# HELPER FUNCTIONS
# ============================================

def format_time(timestamp: str) -> str:
    """Format timestamp for display."""
    if timestamp == "Unknown":
        return "Unknown time"
    try:
        dt = datetime.fromisoformat(timestamp)
        now = datetime.utcnow()
        
        # Calculate relative time
        diff = now - dt.replace(tzinfo=None)
        if diff.total_seconds() < 60:
            return "Just now"
        elif diff.total_seconds() < 3600:
            mins = int(diff.total_seconds() / 60)
            return f"{mins}m ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            return dt.strftime("%b %d, %Y %H:%M")
    except:
        return timestamp

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if "news_search_query" not in st.session_state:
    st.session_state.news_search_query = ""

if "news_results" not in st.session_state:
    st.session_state.news_results = None

if "news_error" not in st.session_state:
    st.session_state.news_error = None

if "twitter_urls" not in st.session_state:
    st.session_state.twitter_urls = {}

# ============================================
# SEARCH SECTION
# ============================================

st.markdown("""
<div class="search-container">
    <h3>🔍 Search News & Social Media</h3>
    <p>Enter a flight number (e.g., <code>AA100</code>, <code>AI203</code>) or keywords (e.g., <code>flight delays</code>)</p>
</div>
""", unsafe_allow_html=True)

# Search input
col1, col2 = st.columns([4, 1])

with col1:
    search_query = st.text_input(
        "Search for flight disruptions",
        placeholder="e.g., AA100, flight delays, Delhi airport",
        value=st.session_state.news_search_query,
        help="Enter a flight number or keywords",
        key="news_search_input"
    )

with col2:
    search_button = st.button("🔎 Search", use_container_width=True)

# ============================================
# SEARCH PROCESSING & DETECTION
# ============================================

if search_button or st.session_state.news_search_query:
    if search_query.strip():
        st.session_state.news_search_query = search_query.strip()
        
        # Detect query type
        is_disruption = detect_disruption_keywords(search_query)
        is_news_request = detect_news_request(search_query)
        inferred_airlines = infer_airlines_from_query(search_query)
        
        # Show detection badges
        st.markdown("---")
        
        detection_cols = st.columns([1, 1, 1, 2])
        
        with detection_cols[0]:
            if is_disruption:
                st.success("🚨 Disruption Detected")
        
        with detection_cols[1]:
            if inferred_airlines:
                st.info(f"✈️ Airlines: {', '.join(inferred_airlines)}")
        
        with detection_cols[2]:
            if is_news_request:
                st.info("📢 News Request")
        
        # ============================================
        # NEWS TABS
        # ============================================
        
        st.markdown("")
        tab1, tab2 = st.tabs(["📰 RSS News", "𝕏 Twitter/X Search"])
        
        # ========================
        # TAB 1: RSS NEWS
        # ========================
        
        with tab1:
            with st.spinner("🔄 Fetching news..."):
                try:
                    api_url = "http://127.0.0.1:5000/api/news/rss"
                    params = {"q": search_query.strip()}
                    
                    response = requests.get(api_url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.news_results = data
                        st.session_state.news_error = None
                        
                        # Parse response
                        items = data.get("items", [])
                        count = data.get("count", 0)
                        is_cached = data.get("cached", False)
                        
                        # Show status info
                        status_cols = st.columns([2, 2, 2])
                        with status_cols[0]:
                            if is_cached:
                                st.caption("⚡ Results from cache (5-min TTL)")
                            else:
                                st.caption("🌐 Live results")
                        with status_cols[1]:
                            st.caption(f"📊 {count} articles found")
                        
                        if not items:
                            st.info("No news articles found. Try different search terms.")
                        else:
                            # Display articles with enhanced styling
                            for idx, item in enumerate(items, 1):
                                st.markdown(f"""
                                <div class="news-card">
                                    <div class="news-title">
                                        <a href="{item.get('link', '#')}" target="_blank">
                                            {idx}. {item.get('title', 'No title')}
                                        </a>
                                    </div>
                                    <div class="news-meta">
                                        <span class="news-meta-item">
                                            <span class="source-badge rss-badge">📌 RSS</span>
                                            {item.get('source', 'Unknown Source')}
                                        </span>
                                        <span class="news-meta-item">
                                            ⏰ {format_time(item.get('publishedAt', 'Unknown'))}
                                        </span>
                                    </div>
                                    <div class="news-snippet">
                                        {item.get('snippet', '')}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    elif response.status_code == 502:
                        error_data = response.json()
                        st.session_state.news_error = error_data.get("message", "Failed to fetch news")
                        st.session_state.news_results = None
                        st.error(f"❌ {st.session_state.news_error}")
                    
                    else:
                        error_msg = f"API error: {response.status_code}"
                        st.session_state.news_error = error_msg
                        st.session_state.news_results = None
                        st.error(f"❌ {error_msg}")
                        
                except requests.ConnectionError:
                    error_msg = "Cannot connect to news server (http://127.0.0.1:5000)"
                    st.session_state.news_error = error_msg
                    st.session_state.news_results = None
                    st.error(f"❌ {error_msg}")
                    st.info("ℹ️ To start the API server, run: `python api_server.py`")
                    
                except requests.Timeout:
                    error_msg = "Request timeout - server took too long to respond"
                    st.session_state.news_error = error_msg
                    st.session_state.news_results = None
                    st.error(f"❌ {error_msg}")
                    
                except Exception as e:
                    error_msg = f"Error fetching news: {str(e)}"
                    st.session_state.news_error = error_msg
                    st.session_state.news_results = None
                    st.error(f"❌ {error_msg}")
        
        # ========================
        # TAB 2: TWITTER/X SEARCH
        # ========================
        
        with tab2:
            st.markdown("**Live Search on Twitter (X)** - Click buttons below to search live on Twitter")
            st.markdown("*These searches use advanced operators for better results*")
            st.markdown("")
            
            twitter_builder = TwitterSearchBuilder()
            
            # Disruption Searches
            st.markdown("**Disruption Searches**")
            
            if search_query.strip():
                airlines = inferred_airlines if inferred_airlines else None
                flight_url = twitter_builder.build_flight_disruption_search(
                    search_query.strip(),
                    airlines=airlines
                )
                
                col1, col2 = st.columns([2, 3])
                with col1:
                    if st.button("🔴 Flight Disruption", key="twitter_flight", use_container_width=True):
                        st.markdown(f'<a href="{flight_url}" target="_blank">Opening Twitter search...</a>', unsafe_allow_html=True)
                
                with col2:
                    st.caption("delay OR diverted OR cancelled")
            
            st.markdown("")
            st.markdown("**News & Updates**")
            
            # General news search
            news_url = twitter_builder.builds_news_disruption_search(search_query.strip())
            
            col1, col2 = st.columns([2, 3])
            with col1:
                if st.button("📰 News & Stories", key="twitter_news", use_container_width=True):
                    st.markdown(f'<a href="{news_url}" target="_blank">Opening Twitter search...</a>', unsafe_allow_html=True)
            
            with col2:
                st.caption("Latest news and updates about the topic")
