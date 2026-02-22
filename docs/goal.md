You are helping me build an AI-powered Flight Disruption Recovery Assistant for a hackathon.

Goal:
Build a fast, intelligent Streamlit chat app that helps passengers or airline staff find the best alternative flights, especially during cancellations due to weather.

Tech stack:

* Python
* Streamlit (chat UI)
* SQLite (local database)
* LangGraph (agent workflow)
* OpenAI or Gemini for LLM
* Pandas
* **OpenSky Network API** (live flight data)
* Must be fast and hackathon-friendly

IMPORTANT PRODUCT RULES:

* Store numeric risk values internally (0–1)
* Show ONLY Low / Medium / High in UI
* Prioritize speed and clarity
* Focus heavily on cancellation recovery flow
* Avoid overengineering
* **Offline/Online Architecture**: Support both cached data (offline) and live sync (online)

---

## 🛰️ LIVE DATA ARCHITECTURE (IMPORTANT)

**Hybrid Offline/Online Model:**

1. **Online Mode (WiFi ON)**:
   - User clicks "Sync Live Planes" button
   - Fetches real-time aircraft from OpenSky Network API
   - Stores snapshot in local SQLite database (`flights.db`)
   - ~150-200 aircraft over India bounding box

2. **Offline Mode (WiFi OFF)**:
   - App continues working with cached data
   - No internet required for queries/searches
   - Database is local file on user's machine
   - Streamlit runs on `localhost:8501` (no external server)

3. **Why This Works**:
   - **SQLite file persistence** - database saved locally
   - **Snapshot model** - not real-time streaming
   - **Think: Downloaded video vs streaming**
   - Once synced, data is cached until next sync

4. **When to Sync**:
   - Before demos/presentations
   - After several hours (data gets stale)
   - Peak flight hours (7-9 AM, 5-7 PM IST) for max aircraft

5. **Data Sources**:
   - **Live Data** (OpenSky): Real aircraft with positions, speed, altitude
   - **Fake Data** (Synthetic): 300 realistic flights for testing
   - Default filter: "Live Only" mode

**This architecture is a key selling point - document it clearly in demos!**

---

## CORE FEATURES

1. Streamlit Chat Interface

Create a clean Streamlit chat UI using:

* st.chat_message
* st.chat_input
* conversation memory

Users can ask queries like:

* "Show flights from Delhi to Pune tomorrow afternoon"
* "My flight AI203 got cancelled"
* "Find alternatives for flight AI203"

Also add a simple input box for:

🚨 Disruption Mode:
User can directly enter a flight_id to trigger recovery flow.

🛰️ Live Data Sync:
Sidebar button "Sync Live Planes (OpenSky)" to fetch real-time aircraft.

---

2. Database Design

Create SQLite database flights.db with table:

CREATE TABLE flights (
flight_id TEXT PRIMARY KEY,

```
source TEXT,
destination TEXT,
date TEXT,
departure_time TEXT,
arrival_time TEXT,

seats_available INTEGER,
price INTEGER,
status TEXT,

fog_risk REAL,
rain_risk REAL,
wind_risk REAL,

airport_congestion REAL,
previous_flight_delay REAL,

delay_probability REAL,

-- New columns for OpenSky integration
data_source TEXT DEFAULT 'fake',  -- 'fake' or 'opensky'
raw_json TEXT,                    -- Original API response
last_updated_utc TEXT             -- Sync timestamp
```

);

Create indexes on:

* source
* destination
* date
* departure_time
* status
* data_source

Also generate a Python script to populate at least 120 realistic Indian domestic flights.

**Live Data Notes:**
- OpenSky flights may have `destination = 'Unknown'` (inferred from nearest city)
- SQL queries must handle "Unknown" destinations gracefully
- Live flights use estimated weather/congestion values

---

3. Risk Label Mapping

Implement global helper:

def risk_label(score):
if score < 0.3:
return "Low"
elif score < 0.6:
return "Medium"
else:
return "High"

Compute overall weather score:

weather_score = (fog_risk + rain_risk + wind_risk) / 3

UI must show ONLY labels, never raw decimals.

---

4. LangGraph Agent Workflow

Create nodes:

* intent_extractor
* sql_generator
* db_query_tool
* ranking_engine
* response_generator

Behavior:

If intent == search_flights:
→ normal filtered search

If intent == recovery:
→ fetch original flight
→ find alternatives
→ rank them

---

5. SQL Generator

Create safe parameterized SQL builder that:

* prevents SQL injection
* supports optional filters
* supports time range filtering
* supports multiple destinations
* is optimized for fast retrieval

---

6. Ranking Engine (CRITICAL)

Implement scoring:

score =
(0.35 * seat_score) +
(0.25 * time_score) +
(0.20 * weather_score_adj) +
(0.10 * congestion_score) +
(0.10 * reliability_score)

Where:

* seat_score increases with seats_available
* time_score prefers afternoon (12–17)
* weather_score_adj = (1 - average weather risk)
* congestion_score = (1 - airport_congestion)
* reliability_score = (1 - delay_probability)

Return top 3 flights.

---

7. Cancellation Recovery Logic (VERY IMPORTANT)

If user provides flight_id OR uses Disruption Mode:

Steps:

1. Fetch original flight
2. Extract route and date
3. Exclude cancelled flight
4. Find alternatives
5. Rank them
6. Present best options

This is the primary demo flow.

---

8. “Why this flight?” Explainability

For EACH suggested flight:

* Add a small button: "Why this flight?"
* When clicked, show short explanation based on ranking factors.

Example output:

"Selected due to low weather risk, available seats, and optimal afternoon timing."

This must be dynamically generated from the scoring logic.

---

9. Smart Edge Case Handling

If no direct flights found:

System should respond:

"No direct flights available. Showing best connecting options."

Simulate simple connecting flight logic if needed.

Handle empty results gracefully.

---

10. Performance Optimization

Use Streamlit caching:

@st.cache_data

Cache:

* database reads
* heavy queries
* flight lookup by id

App must feel instant during demo.

---

11. Response Formatting

Responses must look clean:

Best alternative found:
Flight AI203 — Delhi → Pune — 14:30
Seats: Limited
Weather Risk: Low
Delay Risk: Medium

Never show raw numeric risk values in UI.

---

12. Code Quality

* Modular Python files
* Clear docstrings
* Hackathon friendly
* Include requirements.txt
* Include run instructions
* Avoid unnecessary complexity

Deliver a fully working MVP.

Be practical, clean, and production-minded.
---

## 🔑 KEY ARCHITECTURE POINTS (CRITICAL FOR UNDERSTANDING)

### Offline/Online Capability Explained

**This is the most important architectural feature to understand:**

1. **The app works WITHOUT internet** after initial sync
   - Why? SQLite database (`flights.db`) is a LOCAL FILE
   - Streamlit server runs on `localhost:8501` (YOUR COMPUTER)
   - No cloud servers, no external dependencies for queries

2. **Syncing creates a SNAPSHOT**
   - "Sync Live Planes" downloads current aircraft positions
   - Data is saved to local database
   - **NOT real-time streaming** - it's cached data
   - Like downloading a video to watch offline vs streaming

3. **When you NEED internet:**
   - During initial app launch (first time only)
   - When clicking "Sync Live Planes" button
   - To get fresh/updated aircraft positions

4. **When you DON'T NEED internet:**
   - Searching through synced flights
   - Running disruption recovery
   - Using the chat interface
   - Viewing flight details and rankings

### Demo Talking Points

When presenting this project:

✅ **"This app works completely offline after syncing"**
✅ **"Data is cached locally using SQLite - no cloud required"**
✅ **"Perfect for airline staff in areas with poor connectivity"**
✅ **"Sync fresh data when needed, browse offline when not"**
✅ **"Real-time isn't always needed - snapshots work for most use cases"**

### Why This Architecture Matters

- **Resilience**: App doesn't break if internet drops mid-demo
- **Speed**: Local database queries are instant
- **Privacy**: No data leaves user's machine
- **Hackathon-friendly**: No API rate limits during judging
- **Real-world applicable**: Airlines need offline-capable tools

**REMEMBER:** This is a FEATURE, not a limitation. Many production systems use snapshot-based caching for exactly this reason.