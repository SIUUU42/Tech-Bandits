# ✈️ Flight Disruption Recovery Assistant

**An AI-powered Streamlit chatbot for finding alternative flights during cancellations and delays.**

Built for hackathons with a focus on speed, clarity, and intelligent disruption recovery.

---

## 🎯 Features

### Core Capabilities
- **🚨 Disruption Recovery Mode** - Enter a flight ID and instantly get best alternatives
- **🔍 Smart Flight Search** - Natural language queries for flight searches
- **🤖 Intent Detection** - Automatically understands if you're searching or recovering
- **⭐ Intelligent Ranking** - Flights scored on 5 factors: seats, timing, weather, congestion, reliability
- **💡 Explainability** - Click "Why this flight?" to see scoring breakdown
- **⚡ Lightning Fast** - Caching optimization for instant responses

### Product Features
- Clean Streamlit chat interface
- SQLite database with 150+ realistic Indian domestic flights
- Risk labels (Low/Medium/High) instead of raw numbers
- Afternoon time preference optimization (12-17)
- Airport congestion and delay probability scoring
- Weather risk assessment
- Connecting flight fallback (MVP)

---

## 🛠️ Tech Stack

```
Python 3.10+
Streamlit 1.40+
SQLite3
LangGraph (agent workflow)
Pandas
```

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone <repo-url>
cd Tech-Bandits
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database (Optional)
```bash
python database.py
```
This creates `flights.db` with 150 realistic Indian flights. Run automatically on first app start.

---

## 🚀 Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📝 How to Use

### Mode 1: Natural Language Search
```
User: "Show flights from Delhi to Pune tomorrow afternoon"
→ Agent extracts: source=Delhi, destination=Pune, date=tomorrow, time=afternoon
→ Returns ranked flights with explanations
```

### Mode 2: Disruption Recovery (Main Demo)
```
User: "My flight AI203 got cancelled"
→ Agent fetches original flight
→ Finds alternatives on same route/date
→ Ranks and displays best 3 options
```

### Mode 3: Direct Flight ID (Fastest)
```
1. Enter "AI203" in sidebar Disruption Mode
2. Click "Find Alternatives"
3. Instantly see best recovery options
```

### Mode 4: Click "Why this flight?"
```
Each flight has explainability button
Shows: "Selected due to low weather risk, available seats, and optimal afternoon timing."
```

---

## 🏗️ Architecture

```
app.py
├── Streamlit UI (chat, disruption mode, explainability)
├── Session state management
└── Caching for performance

agent.py (LangGraph-like workflow)
├── intent_extractor: Classify search vs recovery
├── db_query_node: Execute parameterized SQL
├── ranking_node: Score and rank flights
└── response_generator_node: Format for UI

ranking_engine.py
├── Seat availability scoring
├── Time preference scoring (afternoon preferred)
├── Weather risk scoring
├── Congestion scoring
├── Reliability scoring (delay probability inverse)
└── Explainability generation

sql_generator.py
├── Safe parameterized SQL queries
├── Search flights with optional filters
├── Get alternatives for disrupted flights
└── Prevent SQL injection

database.py
├── SQLite schema initialization
├── Flight data generation (150 realistic flights)
├── City and time generation
└── Database seeding

utils.py
├── Risk label mapping (numeric → Low/Medium/High)
├── Weather score calculation
├── Flight display formatting
└── Time preference utilities
```

---

## 🎯 Scoring Formula

Each flight is scored on 5 weighted factors:

```python
score = (0.35 * seat_score) +
        (0.25 * time_score) +
        (0.20 * weather_score_adj) +
        (0.10 * congestion_score) +
        (0.10 * reliability_score)

Where:
- seat_score: Normalized available seats (0-1)
- time_score: Preference for afternoon 12-17 (0-1)
- weather_score_adj: Inverse of weather risk (0-1)
- congestion_score: Inverse of airport congestion (0-1)
- reliability_score: Inverse of delay probability (0-1)
```

**Top 3 flights** are returned to user.

---

## 📊 Database Schema

```sql
CREATE TABLE flights (
    flight_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    date TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    seats_available INTEGER,
    price INTEGER,
    status TEXT,
    fog_risk REAL,
    rain_risk REAL,
    wind_risk REAL,
    airport_congestion REAL,
    previous_flight_delay REAL,
    delay_probability REAL
);

Indexes on: source, destination, date, departure_time, status, flight_id
```

**Sample Data:** 150 flights across 15 Indian cities
- Routes: Delhi, Mumbai, Bangalore, Hyderabad, Chennai, etc.
- Realistic times, prices, and risk values
- Mix of Active/Cancelled flights

---

## ⚡ Performance Optimizations

1. **Streamlit Caching**
   - `@st.cache_resource` - Agent initialization (once per app)
   - `@st.cache_data` - Flight count lookup

2. **Database Optimization**
   - Indexed columns for fast queries
   - Parameterized queries prevent SQL injection
   - Fast city-to-city lookups

3. **Session State**
   - Chat history caching
   - Flight explanations stored
   - Disruption mode quick access

**Result:** Instant response (<200ms) for most queries

---

## 🎨 UI/UX Highlights

- **Clean Chat Interface** - Familiar chat experience
- **Flight Cards** - Formatted with departure, seats, risks, price
- **Color-coded Risks** - Low/Medium/High labels (no raw numbers)
- **Explainability Buttons** - "Why this flight?" on each option
- **Disruption Sidebar** - Quick access for emergency recovery
- **Responsive Layout** - Works on desktop and tablet

---

## 🧪 Testing

### Test Recovery Flow
```bash
python agent.py
# Output: Test recovery and search modes
```

### Test Database
```bash
python database.py
# Output: Database initialization and flight count
```

### Test Ranking
```bash
python ranking_engine.py
# Output: Ranking scores and explanations
```

---

## 🚀 Hackathon Tips

1. **Start with Disruption Mode** - Most impressive demo
   - Enter "AI203" → See instant recovery options
   - Shows ranking intelligence clearly

2. **Show Weather/Reliability Scoring** - Judges love explainability
   - Click "Why this flight?" buttons
   - Demonstrates ML thinking

3. **Highlight Speed** - Instant responses are impressive
   - All cached operations show system efficiency
   - Database queries are optimized

4. **City Variety** - Show searching across multiple Indian cities
   - 15 cities in database
   - Demonstrates realistic scale

---

## 📋 Code Quality

- ✅ Modular architecture (7 focused Python files)
- ✅ Clear docstrings on all functions
- ✅ Type hints throughout
- ✅ Error handling and logging
- ✅ SQLite injection prevention
- ✅ Production-ready Streamlit patterns
- ✅ No overengineering - pure MVP focus

---

## 🔧 Customization

### Change Weight Distribution
Edit `ranking_engine.py`:
```python
SEAT_WEIGHT = 0.35      # Increase for seat availability priority
TIME_WEIGHT = 0.25      # Increase for timing preference
WEATHER_WEIGHT = 0.20   # Increase for weather priority
```

### Add More Flights
Edit `database.py`:
```python
flights = generate_flights(300)  # Generate 300 instead of 150
```

### Change Time Preferences
Edit `utils.py`:
```python
time_preference_score()  # Modify afternoon window
```

---

## ⚠️ Known Limitations (MVP)

- Connecting flights are simulated (placeholder)
- Single-leg flights only in actual ranking
- Date range limited to next 7 days
- Single LLM not integrated yet (agent is rule-based)
- No real weather API integration

**These are intentionally simplified for hackathon speed!**

---

## 📄 File Manifest

```
Tech-Bandits/
├── app.py                 (Streamlit UI - main entry point)
├── agent.py              (LangGraph-like agent workflow)
├── ranking_engine.py     (Flight scoring and ranking)
├── sql_generator.py      (Safe SQL query builder)
├── database.py           (SQLite schema and seeding)
├── utils.py              (Utility functions)
├── requirements.txt      (Python dependencies)
├── README.md             (This file)
└── flights.db            (SQLite database - auto-generated)
```

---

## 👥 Team

Built with ❤️ for hackathon by Team Tech-Bandits

---

## 📝 License

Open source - use freely for learning and development.

---

## 🎉 Ready to Demo!

```bash
# Final checklist
1. pip install -r requirements.txt
2. streamlit run app.py
3. Try disruption mode: "AI203"
4. Show search: "Delhi to Pune tomorrow"
5. Click "Why this flight?" - BOOM! 🚀
```

Good luck at the hackathon! 🏆
