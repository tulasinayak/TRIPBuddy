"""
brain.py — Orchestrator / Planner Agent
Parses user query → dispatches to sub-agents → aggregates results
"""

from schema import TravelPlan
from utils import extract_json, pretty_print_plan
from executor import execute_tasks
from llm import get_llm

llm = get_llm()

BRAIN_PROMPT = """
You are the Brain of a multi-agent travel planning system.

Your job:
1. Understand the user's travel query
2. Extract structured data
3. Decide which specialist agents to activate

Extract these fields:
- destination (string)
- days (integer)
- budget (integer, per day per person in euros)
- persons (integer, default 1)
- interests (list of strings)

Available tasks:
- find_stays         → always include
- plan_itinerary     → always include
- recommend_food     → include if user mentions food, dining, restaurants, or cuisine
- travel_tips        → always include for international travel
- transport_options  → include if user asks about getting around or transport
- weather_info       → include if user mentions weather or seasons
- narrator_script    → include if user mentions audio guide, narration, or storytelling

Rules:
- Always include: find_stays, plan_itinerary, travel_tips
- Default persons to 1 if not specified
- Budget is per day per person
- Return STRICT JSON only — no explanation, no markdown, no extra text

Example:
User: 2 days in Rome, budget 100 euros, love history and food

Output:
{
  "destination": "Rome",
  "days": 2,
  "budget": 100,
  "persons": 1,
  "interests": ["history", "food"],
  "tasks": ["find_stays", "plan_itinerary", "recommend_food", "travel_tips"]
}
"""


def brain(user_input: str) -> dict:
    print(f"\n{'='*60}")
    print(f"🧠 BRAIN AGENT — Processing query")
    print(f"{'='*60}")
    print(f"Input: {user_input}\n")

    prompt = f"{BRAIN_PROMPT}\n\nUser: {user_input}"
    response = llm.invoke(prompt)

    print("📤 Raw Brain Output:")
    print(response)

    data = extract_json(response)
    plan = TravelPlan(**data)

    print(f"\n✅ Structured Plan:")
    print(f"  Destination : {plan.destination}")
    print(f"  Days        : {plan.days}")
    print(f"  Budget      : €{plan.budget}/day/person")
    print(f"  Persons     : {plan.persons}")
    print(f"  Interests   : {', '.join(plan.interests)}")
    print(f"  Tasks       : {plan.tasks}")

    results = execute_tasks(plan)

    print(f"\n{'='*60}")
    print("📦 FINAL TRAVEL PLAN")
    print(f"{'='*60}")
    pretty_print_plan(results)

    return results


if __name__ == "__main__":
    query = "2 days in Rome, budget 100 euros, love history and food"
    brain(query)