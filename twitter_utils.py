"""
Twitter search URL builder with query operators.

Builds search URLs with operators: quotes, OR, from:, lang:, etc.
"""

from urllib.parse import quote
from typing import Optional, List


class TwitterSearchBuilder:
    """Build Twitter search URLs with advanced query operators."""
    
    def __init__(self):
        """Initialize Twitter search builder."""
        self.base_url = "https://twitter.com/search?q="
    
    def build_flight_disruption_search(
        self,
        flight_number: str,
        airlines: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> str:
        """
        Build Twitter search URL for flight disruptions.
        
        Args:
            flight_number: Flight number (e.g., AA100, AI203)
            airlines: List of airline handles (e.g., ["AmericanAir", "SpiceJet"])
            keywords: Additional keywords (e.g., ["delay", "cancelled", "diverted"])
            
        Returns:
            Twitter search URL
        """
        query_parts = [flight_number]
        
        # Add disruption keywords
        if keywords:
            keyword_phrase = " OR ".join(keywords)
            query_parts.append(f"({keyword_phrase})")
        else:
            # Default disruption keywords
            query_parts.append("(delay OR diverted OR cancelled)")
        
        # Add airline filters
        if airlines:
            airline_filters = " OR ".join([f"from:{airline}" for airline in airlines])
            query_parts.append(f"({airline_filters})")
        
        # Add live filter
        query_parts.append("&f=live")
        
        query = " ".join(query_parts)
        encoded_query = quote(query, safe="")
        
        return self.base_url + encoded_query + query_parts[-1]
    
    def build_keyword_search(
        self,
        keywords: List[str],
        airlines: Optional[List[str]] = None,
        lang: str = "en"
    ) -> str:
        """
        Build Twitter search URL for keyword search.
        
        Args:
            keywords: List of keywords to search
            airlines: Optional airline handles to filter by
            lang: Language code (default: en)
            
        Returns:
            Twitter search URL
        """
        # Build keyword phrase with OR
        keyword_phrase = " OR ".join(keywords)
        query_parts = [f"({keyword_phrase})"]
        
        # Add airline filters
        if airlines:
            airline_filters = " OR ".join([f"from:{airline}" for airline in airlines])
            query_parts.append(f"({airline_filters})")
        
        # Add language filter
        query_parts.append(f"lang:{lang}")
        
        # Add live filter
        query_parts.append("&f=live")
        
        query = " ".join(query_parts)
        encoded_query = quote(query, safe="")
        
        return self.base_url + encoded_query + query_parts[-1]
    
    def builds_news_disruption_search(self, query: str) -> str:
        """
        Build Twitter search for general news/disruption queries.
        
        Args:
            query: Search query
            
        Returns:
            Twitter search URL
        """
        # Add news-related filters
        query_with_filters = f'"{query}" (news OR disruption OR delay OR cancelled)'
        encoded_query = quote(query_with_filters, safe="")
        
        return self.base_url + encoded_query + "&f=live"


def infer_airlines_from_query(query: str) -> List[str]:
    """
    Try to infer airlines from flight number or query.
    
    Args:
        query: User search query
        
    Returns:
        List of airline Twitter handles
    """
    query_upper = query.upper()
    
    # Map flight prefixes to airline handles
    airline_map = {
        "AA": "AmericanAir",
        "UA": "United",
        "DL": "Delta",
        "SW": "SouthwestAir",
        "B6": "JetBlue",
        "AI": "SpiceJet",  # Air India in India
        "SG": "SpiceJet",
        "6E": "IndiGo",
        "UK": "vistara",
        "BA": "british_airways",
        "LH": "lufthansa",
        "AF": "FrenchBee",
        "KL": "KLMPersonal",
        "QA": "qatar_airways",
        "EK": "emirates",
    }
    
    detected_airlines = []
    for prefix, handle in airline_map.items():
        if query_upper.startswith(prefix):
            detected_airlines.append(handle)
            break
    
    return detected_airlines


def detect_disruption_keywords(query: str) -> bool:
    """
    Detect if query contains disruption-related keywords.
    
    Args:
        query: User search query
        
    Returns:
        True if disruption keywords detected
    """
    disruption_keywords = [
        "disruption", "disrupted",
        "cancelled", "canceled",
        "delayed", "delay",
        "diverted", "diversion",
        "cancelled", "cancellation",
        "stranded", "grounded",
        "rebooked"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in disruption_keywords)


def detect_news_request(query: str) -> bool:
    """
    Detect if query is a news request.
    
    Args:
        query: User search query
        
    Returns:
        True if news request detected
    """
    news_keywords = ["news", "report", "update", "alert", "help"]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in news_keywords)


if __name__ == "__main__":
    builder = TwitterSearchBuilder()
    
    # Test flight disruption search
    print("Test 1: Flight disruption search")
    url = builder.build_flight_disruption_search("AA100", airlines=["AmericanAir"])
    print(f"URL: {url}\n")
    
    # Test keyword search
    print("Test 2: Keyword search")
    url = builder.build_keyword_search(["flight delays", "weather"], airlines=["Delta"])
    print(f"URL: {url}\n")
    
    # Test detection
    print("Test 3: Keyword detection")
    query = "AI203 delayed"
    print(f"Query: {query}")
    print(f"Is disruption: {detect_disruption_keywords(query)}")
    print(f"Inferred airlines: {infer_airlines_from_query(query)}")
