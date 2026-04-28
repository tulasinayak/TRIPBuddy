"""
executor.py — Task dispatcher
Routes tasks from the Brain to the appropriate specialist agents.
"""

from schema import TravelPlan
from llm import get_llm
from agents.stays_agent import StaysAgent
from agents.itinerary_agent import ItineraryAgent
from agents.food_agent import FoodAgent
from agents.tips_agent import TipsAgent
from agents.transport_agent import TransportAgent
from agents.weather_agent import WeatherAgent
from agents.narrator_agent import NarratorAgent

# Task → Agent class mapping
AGENT_REGISTRY = {
    "find_stays":        StaysAgent,
    "plan_itinerary":    ItineraryAgent,
    "recommend_food":    FoodAgent,
    "travel_tips":       TipsAgent,
    "transport_options": TransportAgent,
    "weather_info":      WeatherAgent,
    "narrator_script":   NarratorAgent,
}

# Preferred execution order
TASK_ORDER = [
    "weather_info",
    "find_stays",
    "transport_options",
    "plan_itinerary",
    "recommend_food",
    "travel_tips",
    "narrator_script",  # Last — uses context from other agents
]


def execute_tasks(plan: TravelPlan) -> dict:
    """
    Execute all tasks from the plan in order.
    Returns a dict of {task_name: result_string}.
    """
    llm = get_llm()
    results = {}

    # Sort tasks by preferred order
    tasks_to_run = sorted(
        plan.tasks,
        key=lambda t: TASK_ORDER.index(t) if t in TASK_ORDER else 99
    )

    print(f"\n{'='*60}")
    print(f"🧩 EXECUTOR — Running {len(tasks_to_run)} tasks")
    print(f"{'='*60}")

    for task in tasks_to_run:
        if task not in AGENT_REGISTRY:
            print(f"  ⚠️  Unknown task: '{task}' — skipping")
            continue

        AgentClass = AGENT_REGISTRY[task]
        agent = AgentClass(llm=llm)

        print(f"\n  ▶ Running: {agent.name}")

        try:
            # Pass accumulated results to narrator so it can reference them
            if task == "narrator_script":
                result = agent.run(plan, context=results)
            else:
                result = agent.run(plan)

            results[task] = result
            print(f"  ✅ {agent.name} — done ({len(result)} chars)")

        except Exception as e:
            error_msg = f"[{agent.name} failed: {str(e)}]"
            results[task] = error_msg
            print(f"  ❌ {agent.name} — error: {e}")

    return results