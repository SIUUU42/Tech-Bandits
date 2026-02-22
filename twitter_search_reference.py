"""
Quick reference for Twitter search operators and flight disruption queries.
"""

TWITTER_SEARCH_EXAMPLES = {
    "Flight Disruptions": [
        {
            "query": "AA100 (delay OR cancelled OR diverted) from:AmericanAir",
            "meaning": "Flight AA100 disruptions from American Airlines",
            "use_case": "Flight-specific disruption updates"
        },
        {
            "query": "(flight delay OR flight cancellation) lang:en since:2026-02-22",
            "meaning": "Recent flight disruption mentions in English",
            "use_case": "General disruption news"
        },
        {
            "query": "\"airport closure\" OR \"airport disruption\" lang:en",
            "meaning": "Airport closure announcements",
            "use_case": "Major airport issues"
        }
    ],
    
    "Airline Status Updates": [
        {
            "query": "from:AmericanAir (delay OR cancelled OR weather)",
            "meaning": "American Airlines official updates",
            "use_case": "Official airline statements"
        },
        {
            "query": "from:Delta OR from:United (operational update)",
            "meaning": "Official updates from multiple airlines",
            "use_case": "Major operational news"
        }
    ],
    
    "Weather Impact": [
        {
            "query": "flight delay weather storm",
            "meaning": "Flight delays caused by weather",
            "use_case": "Weather-related disruptions"
        },
        {
            "query": "(snow OR storm OR thunderstorm) flight -ski",
            "meaning": "Weather events affecting flights (excluding ski content)",
            "use_case": "Severe weather updates"
        }
    ],
    
    "Airport-Specific": [
        {
            "query": "\"Denver airport\" OR \"Denver International\" (delay OR closed)",
            "meaning": "Issues at specific airport",
            "use_case": "Airport operations tracking"
        },
        {
            "query": "Delhi airport OR Indira Gandhi (disruption OR delay OR issue)",
            "meaning": "Indian airport issues",
            "use_case": "India focus"
        }
    ]
}

TWITTER_OPERATORS = {
    "OR": {
        "syntax": "term1 OR term2",
        "example": "delay OR cancelled",
        "meaning": "Either condition (returns more results)"
    },
    
    "from:": {
        "syntax": "from:username",
        "example": "from:AmericanAir",
        "meaning": "Tweets from specific account"
    },
    
    "Exact Phrase": {
        "syntax": '"exact phrase"',
        "example": '"flight delay"',
        "meaning": "Exact phrase match (very specific)"
    },
    
    "Exclude (-) ": {
        "syntax": "-word",
        "example": "flight -delay",
        "meaning": "Exclude tweets containing word"
    },
    
    "lang:": {
        "syntax": "lang:code",
        "example": "lang:en",
        "meaning": "Filter by language (en, es, fr, etc.)"
    },
    
    "since:": {
        "syntax": "since:YYYY-MM-DD",
        "example": "since:2026-02-22",
        "meaning": "Tweets from date onwards"
    },
    
    "&f=live": {
        "syntax": "&f=live",
        "example": "query&f=live",
        "meaning": "Show live results only"
    }
}

AIRLINE_TWITTER_HANDLES = {
    # International
    "AA": "@AmericanAir",
    "BA": "@british_airways",
    "DL": "@Delta",
    "LH": "@lufthansa",
    "UA": "@United",
    "EK": "@emirates",
    "AF": "@FrenchBee",
    "KL": "@KLMPersonal",
    "QA": "@qatar_airways",
    "SQ": "@singaporeair",
    "TG": "@ThaiAirways",
    "VS": "@FlyVirginAtl",
    
    # Indian
    "AI": "@FlyAI",  # Air India
    "SG": "@FlySpiceJet",  # SpiceJet
    "6E": "@IndiGo",  # IndiGo
    "UK": "@vistara",  # Vistara
    "9I": "@allianceair",  # Alliance Air
    "G8": "@GoAirIndia",  # GoAir
}

FLIGHT_PREFIX_TO_AIRLINE = {
    "AA": "American Airlines",
    "BA": "British Airways",
    "DL": "Delta",
    "LH": "Lufthansa",
    "UA": "United",
    "EK": "Emirates",
    "AF": "Air France",
    "KL": "KLM",
    "QA": "Qatar Airways",
    "SQ": "Singapore Airlines",
    "TG": "Thai Airways",
    
    # Indian Airlines
    "AI": "Air India",
    "SG": "SpiceJet",
    "6E": "IndiGo",
    "UK": "Vistara",
    "9I": "Alliance Air",
    "G8": "GoAir",
}

DISRUPTION_KEYWORDS = [
    "delay", "delayed", "delaying",
    "cancel", "cancelled", "cancellation",
    "diverted", "diversion",
    "stranded",
    "grounded",
    "rebooked", "rebooking",
    "weather", "storm", "snow",
    "mechanical", "technical",
    "disruption", "disrupted",
    "incident", "emergency",
    "closure", "closed",
]

# Building search queries
def build_flight_search(flight_number, airline_handle=None):
    """Build optimized flight disruption search."""
    disruption_keywords = ["delay", "diverted", "cancelled"]
    query = f"{flight_number} ({' OR '.join(disruption_keywords)})"
    
    if airline_handle:
        query += f" from:{airline_handle}"
    
    return query + "&f=live"

# Example usage:
if __name__ == "__main__":
    print("Flight Search Examples:")
    print("=" * 60)
    
    for category, examples in TWITTER_SEARCH_EXAMPLES.items():
        print(f"\n{category}:")
        for ex in examples:
            print(f"  Query: {ex['query']}")
            print(f"  Meaning: {ex['meaning']}")
            print(f"  Use: {ex['use_case']}\n")
    
    print("\n" + "=" * 60)
    print("Operators Reference:")
    print("=" * 60)
    
    for op, details in TWITTER_OPERATORS.items():
        print(f"\n{op}")
        print(f"  Syntax: {details['syntax']}")
        print(f"  Example: {details['example']}")
        print(f"  Meaning: {details['meaning']}")
