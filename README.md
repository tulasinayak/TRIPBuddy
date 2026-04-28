# ✈️ TRIPBuddy — AI Travel Planner

A multi-agent AI system that turns a simple travel query into a complete trip plan.

**Type:** `2 days in Rome, budget €100/day, love history and food`  
**Get:** Accommodation, itinerary, food spots, transport, tips, weather, and an audio guide.

---

## 🤖 How It Works

A **Brain Agent** reads your query and dispatches 7 specialist agents:

| Agent | What it does |
|---|---|
| 🏨 Stay Finder | Hotels, hostels & apartments with Airbnb / Booking.com links |
| 🗺️ Itinerary | Day-by-day plan with morning / afternoon / evening blocks |
| 🍽️ Food & Dining | Restaurants with Google Maps & TripAdvisor links |
| ⚡ Travel Tips | Culture, safety, money, apps |
| 🚇 Transport | Airport transfer, local transit, passes |
| ☀️ Weather | Forecast + packing list |
| 🎧 Audio Guide | Cinematic narration script with ambient sounds |

---

## 🚀 Setup

**1. Clone**
```bash
git clone https://github.com/tulasinayak/TRIPBuddy.git
cd TRIPBuddy
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set your LLM**
```bash
# Free local option (install Ollama from ollama.com first)
set TRAVEL_LLM=ollama

# Or Anthropic
set TRAVEL_LLM=anthropic
set ANTHROPIC_API_KEY=your-key-here

# Or OpenAI
set TRAVEL_LLM=openai
set OPENAI_API_KEY=your-key-here
```

**4. Run**
```bash
uvicorn server:app --reload --port 8000
```

**5. Open** → [http://localhost:8000](http://localhost:8000)

---

## 🎧 Audio Guide

The Audio Guide agent generates a full 8–10 minute narration script.  
For a human-sounding voice, add an [ElevenLabs](https://elevenlabs.io) API key in the audio bar (free tier available).  
Without a key it falls back to your browser's built-in voice.

---

## 🛠️ Tech Stack

- **Python** — FastAPI, Pydantic, LangChain
- **LLMs** — Anthropic Claude / OpenAI / Ollama (local)
- **Frontend** — Vanilla HTML/CSS/JS (no framework)
- **TTS** — ElevenLabs API + Web Speech API fallback
- **Audio** — Web Audio API for ambient sounds

---

## 📁 Structure

```
TRIPBuddy/
├── app.html          # Frontend
├── server.py         # FastAPI server
├── brain.py          # Orchestrator agent
├── executor.py       # Task dispatcher
├── llm.py            # LLM factory (Ollama / Anthropic / OpenAI)
├── schema.py         # Pydantic data models
├── utils.py          # Helpers
└── agents/           # 7 specialist agents
```

---

## 👤 Author

**Tulasi Nayak** — [LinkedIn](https://linkedin.com/in/tulasi-nayak) · [GitHub](https://github.com/tulasinayak)
