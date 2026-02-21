# Flight Disruption Recovery Assistant - Quick Start

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
streamlit run app.py
```

### Step 3: Demo Time!

The app will open at `http://localhost:8501`

---

## 💡 What to Demo

### Demo 1: Disruption Recovery (The Wow Factor!)
1. Look at sidebar → **Disruption Mode**
2. See a list of active flights in database
3. Enter any flight ID
4. Click "Find Alternatives"
5. See instant recovery recommendations with explanations

**Why judges love this:** Shows real-world problem solving and AI thinking.

---

### Demo 2: Natural Language Search
1. In chat, type: `"Show flights from Delhi to Mumbai afternoon"`
2. Agent instantly extracts search parameters
3. Returns best 3 ranked flights
4. Click "Why this flight?" for explainability

**Why judges love this:** NLP + ranking algorithm visible together.

---

### Demo 3: Click "Why this flight?"
On any flight card, click the button to see:
```
"Selected due to excellent seat availability, optimal afternoon timing, 
low weather risk, and high on-time reliability."
```

**Why judges love this:** Explainability is critical for AI trust.

---

## 📊 Key Architecture Highlights

### The Agent Workflow
```
User Input 
  ↓
Intent Extractor (Search vs Recovery)
  ↓
SQL Query Builder (Safe, parameterized)
  ↓
Database Query (Indexed for speed)
  ↓
Ranking Engine (5-factor weighted scoring)
  ↓
Response Generator (Markdown formatting)
  ↓
Streamlit UI (Chat + Cards + Explainability)
```

### Scoring Formula
```
score = (0.35 × seats) 
      + (0.25 × afternoon_time) 
      + (0.20 × low_weather_risk)
      + (0.10 × low_congestion)
      + (0.10 × high_reliability)
```

---

## 🎯 File Breakdown

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI (main entry) |
| `agent.py` | Intent + workflow orchestration |
| `ranking_engine.py` | Flight scoring algorithm |
| `sql_generator.py` | Safe DB queries |
| `database.py` | Schema + seeding |
| `utils.py` | Helpers (risk labels, etc) |
| `requirements.txt` | Dependencies |

---

## ⚡ Performance Stats

- ✅ **Database:** 150 flights, indexed queries
- ✅ **Response Time:** <200ms for searches
- ✅ **Caching:** Agent + flight count cached
- ✅ **Cities:** 15 Indian cities for routing
- ✅ **Code:** 700 lines, zero external APIs

---

## 🐛 Troubleshooting

### "Address already in use" error
```bash
# Kill existing Streamlit process
lsof -ti:8501 | xargs kill -9
streamlit run app.py
```

### No flights found in search
- Make sure the source/destination cities are in the database
- Available cities: Delhi, Mumbai, Bangalore, Hyderabad, Chennai, Kolkata, Pune, Ahmedabad, Jaipur, Lucknow, Kochi, Indore, Chandigarh, Goa, Visakhapatnam

### Database issues
```bash
# Reinitialize database
rm flights.db
python database.py
```

---

## 🏆 Hackathon Winning Tips

1. **Lead with disruption mode** - Most impressive UX
2. **Highlight open-sourced code** - Show architecture
3. **Mention the scoring formula** - Judges love AI methods
4. **Show multiple searches** - Proves robustness
5. **Explain explainability** - "Why this flight?" is gold

---

## 🎓 What Makes This Hackathon-Ready

✅ **Complete MVP** - All features working
✅ **Clean Code** - Modular, typed, documented
✅ **Fast Setup** - No complex dependencies
✅ **Real UX** - Chat + disruption modes
✅ **Explainable AI** - Not a black box
✅ **Production Pattern** - Caching + error handling

---

Good luck! 🚀

Questions? Check `goal.md` for full specs or `README.md` for deep dive.
