"""
Flask API server for RSS feed parsing and disruption news.

Provides endpoint: GET /api/news/rss?q=<query>
- Fetches Google News RSS feed
- Parses into JSON items
- Caches results for 5 minutes
- Returns sorted by publishedAt (desc), limited to 20 items
"""

import threading
import time
from datetime import datetime, timedelta
from urllib.parse import quote, urlencode
from typing import Dict, List, Optional, Any
import logging

import feedparser
import requests
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory cache with TTL (5 minutes)
CACHE_TTL_SECONDS = 300
cache: Dict[str, Dict[str, Any]] = {}
cache_lock = threading.Lock()


def clear_expired_cache():
    """Remove expired cache entries."""
    with cache_lock:
        now = time.time()
        expired_keys = [k for k, v in cache.items() if v["expires_at"] < now]
        for key in expired_keys:
            del cache[key]


def get_cached(query: str) -> Optional[Dict[str, Any]]:
    """Get cached result if available and not expired."""
    clear_expired_cache()
    with cache_lock:
        if query in cache:
            return cache[query]["data"]
    return None


def set_cache(query: str, data: Dict[str, Any]):
    """Cache result with 5-minute TTL."""
    with cache_lock:
        cache[query] = {
            "data": data,
            "expires_at": time.time() + CACHE_TTL_SECONDS
        }


def build_google_news_url(query: str) -> str:
    """
    Build Google News RSS feed URL.
    
    Args:
        query: Search query (flight number or keyword)
        
    Returns:
        Google News RSS URL
    """
    # URL encode the query
    encoded_query = quote(query, safe="")
    # Google News RSS endpoint
    return f"https://news.google.com/rss/search?q={encoded_query}&ceid=US:en&hl=en"


def parse_rss_feed(url: str, timeout: int = 10) -> List[Dict[str, str]]:
    """
    Fetch and parse RSS feed.
    
    Args:
        url: RSS feed URL
        timeout: Request timeout in seconds
        
    Returns:
        List of parsed items with fields: title, link, publishedAt, source, snippet
        
    Raises:
        Exception: If fetch/parse fails
    """
    try:
        # Fetch RSS with timeout
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'FlightDisruptionAssistant/1.0'
        })
        response.raise_for_status()
        
        # Parse RSS
        feed = feedparser.parse(response.content)
        
        if feed.bozo and feed.bozo_exception:
            logger.warning(f"RSS parsing warning: {feed.bozo_exception}")
        
        items = []
        for entry in feed.entries[:20]:  # Limit to 20 items
            # Extract fields with fallbacks
            title = entry.get("title", "No title")
            link = entry.get("link", "")
            
            # Parse published date
            published_at = "Unknown"
            if "published" in entry:
                try:
                    # feedparser provides parsed_date as time.struct_time
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        dt = datetime(*entry.published_parsed[:6])
                        published_at = dt.isoformat()
                    else:
                        published_at = entry.get("published", "Unknown")
                except Exception as e:
                    logger.warning(f"Date parse error: {e}")
                    published_at = entry.get("published", "Unknown")
            
            # Extract source (from Google News, often in title or separate field)
            source = "Unknown Source"
            if "source" in entry:
                source = entry["source"].get("title", "Unknown Source")
            
            # Extract snippet/summary
            snippet = entry.get("summary", entry.get("description", "No summary"))
            # Clean HTML tags if present
            if snippet:
                snippet = snippet.replace("<b>", "").replace("</b>", "")
                snippet = snippet.replace("<i>", "").replace("</i>", "")
                # Truncate to 200 chars
                snippet = snippet[:200] + "..." if len(snippet) > 200 else snippet
            
            items.append({
                "title": title,
                "link": link,
                "publishedAt": published_at,
                "source": source,
                "snippet": snippet
            })
        
        # Sort by publishedAt (descending) - newest first
        items.sort(key=lambda x: x["publishedAt"], reverse=True)
        
        return items
        
    except requests.Timeout:
        raise Exception(f"RSS fetch timeout after {timeout}s")
    except requests.RequestException as e:
        raise Exception(f"RSS fetch failed: {str(e)}")
    except Exception as e:
        raise Exception(f"RSS parse failed: {str(e)}")


@app.route("/api/news/rss", methods=["GET"])
def get_news_rss():
    """
    API endpoint to fetch and parse disruption news.
    
    Query Parameters:
        q: Search query (flight number or keyword)
        
    Returns:
        JSON: { query, items: [ { title, link, publishedAt, source, snippet } ] }
        
    Error:
        502: If RSS fetch fails
    """
    query = request.args.get("q", "").strip()
    
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    
    try:
        # Check cache first
        cached_result = get_cached(query)
        if cached_result:
            logger.info(f"Cache hit for query: {query}")
            return jsonify(cached_result), 200
        
        logger.info(f"Fetching RSS for query: {query}")
        
        # Build Google News URL
        rss_url = build_google_news_url(query)
        
        # Fetch and parse RSS
        items = parse_rss_feed(rss_url, timeout=10)
        
        # Build response
        result = {
            "query": query,
            "items": items,
            "count": len(items),
            "cached": False
        }
        
        # Cache the result
        set_cache(query, result)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching RSS for '{query}': {str(e)}")
        return jsonify({
            "error": str(e),
            "message": "Failed to fetch disruption news. Please try again later."
        }), 502


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    logger.info("Starting Flight Disruption News API Server...")
    logger.info("Endpoints:")
    logger.info("  GET /api/news/rss?q=<query>")
    logger.info("  GET /api/health")
    
    # Run Flask on port 5000
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
