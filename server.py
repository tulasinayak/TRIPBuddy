"""
server.py — FastAPI server for TripMind frontend

Endpoints:
  GET  /              → serves app.html
  POST /parse         → parses plain-English query into TravelPlan JSON
  POST /run-single    → runs ONE agent and returns its result
  POST /run           → runs ALL selected agents (batch)
  POST /save          → saves plan to output/ folder as markdown
  GET  /health        → health check

Run:
  uvicorn server:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os

from schema import TravelPlan
from executor import AGENT_REGISTRY, TASK_ORDER
from utils import extract_json, save_plan_to_file
from llm import get_llm

app = FastAPI(title="TripMind")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ──

class ParseRequest(BaseModel):
    query: str

class SingleAgentRequest(BaseModel):
    destination: str
    days: int
    budget: int
    persons: int = 1
    interests: List[str] = []
    task: str                        # single task key e.g. "find_stays"
    prior_results: Dict[str, str] = {}

class BatchRequest(BaseModel):
    destination: str
    days: int
    budget: int
    persons: int = 1
    interests: List[str] = []
    tasks: List[str] = []

class SaveRequest(BaseModel):
    plan: Dict[str, Any]
    results: Dict[str, str]


# ── Shared LLM prompt for parsing ──

BRAIN_SYS = """You are a travel query parser.
Extract JSON with these keys:
  destination (string)
  days        (integer)
  budget      (integer, euros per day per person)
  persons     (integer, default 1)
  interests   (list of strings)
  tasks       (empty list — always [])

Return STRICT JSON only. No markdown, no backticks, no explanation."""


# ── Routes ──

@app.get("/")
def serve_frontend():
    """Serve the app.html file."""
    if not os.path.exists("app.html"):
        raise HTTPException(status_code=404, detail="app.html not found — make sure it's in the same folder as server.py")
    return FileResponse("app.html")


@app.post("/parse")
def parse_query(req: ParseRequest):
    """
    Parse a plain-English travel query into structured JSON.
    The frontend calls this first before running any agents.
    """
    llm = get_llm()
    prompt = f"{BRAIN_SYS}\n\nUser query: {req.query}"
    response = llm.invoke(prompt)

    try:
        data = extract_json(response)
        data.setdefault("tasks", [])
        data.setdefault("persons", 1)
        data.setdefault("interests", [])
        # Validate with Pydantic
        plan = TravelPlan(**data)
        return plan.model_dump()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse query: {e}\nRaw LLM output: {response}")


@app.post("/run-single")
def run_single_agent(req: SingleAgentRequest):
    """
    Run ONE agent and return its result.
    The frontend calls this once per agent so cards fill in one-by-one.
    """
    if req.task not in AGENT_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown task: '{req.task}'")

    plan = TravelPlan(
        destination=req.destination,
        days=req.days,
        budget=req.budget,
        persons=req.persons,
        interests=req.interests,
        tasks=[req.task],
    )

    llm = get_llm()
    AgentClass = AGENT_REGISTRY[req.task]
    agent = AgentClass(llm=llm)

    try:
        if req.task == "narrator_script":
            result = agent.run(plan, context=req.prior_results)
        else:
            result = agent.run(plan)
        return {"result": result, "task": req.task, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{agent.name} failed: {e}")


@app.post("/run")
def run_all_agents(req: BatchRequest):
    """
    Run ALL selected agents in order and return all results.
    Fallback if the frontend uses batch mode.
    """
    plan = TravelPlan(
        destination=req.destination,
        days=req.days,
        budget=req.budget,
        persons=req.persons,
        interests=req.interests,
        tasks=req.tasks,
    )

    llm = get_llm()
    results = {}

    ordered_tasks = sorted(
        plan.tasks,
        key=lambda t: TASK_ORDER.index(t) if t in TASK_ORDER else 99
    )

    for task in ordered_tasks:
        if task not in AGENT_REGISTRY:
            results[task] = f"[Unknown task: {task}]"
            continue
        AgentClass = AGENT_REGISTRY[task]
        agent = AgentClass(llm=llm)
        try:
            if task == "narrator_script":
                result = agent.run(plan, context=results)
            else:
                result = agent.run(plan)
            results[task] = result
        except Exception as e:
            results[task] = f"[{agent.name} failed: {e}]"

    return {"success": True, "results": results}


@app.post("/save")
def save_plan(req: SaveRequest):
    """
    Save the completed travel plan to output/ as a markdown file.
    Called when the user has the auto-save toggle enabled.
    """
    try:
        # Reconstruct a minimal plan object for save_plan_to_file
        class _Plan:
            destination = req.plan.get("destination", "trip")
            days        = req.plan.get("days", 1)
            budget      = req.plan.get("budget", 0)
            persons     = req.plan.get("persons", 1)
            interests   = req.plan.get("interests", [])
            total_budget = budget * days * persons

        filename = save_plan_to_file(_Plan(), req.results)
        return {"success": True, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {e}")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm": os.environ.get("TRAVEL_LLM", "ollama"),
        "model": os.environ.get("OLLAMA_MODEL") or os.environ.get("ANTHROPIC_MODEL") or os.environ.get("OPENAI_MODEL", "default"),
    }