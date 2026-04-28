"""
selective_run.py — Run only the agents you choose.

Usage (interactive menu):
  python selective_run.py

Usage (pass agents directly):
  python main.py --agents itinerary food
  python main.py --agents itinerary tips --save
  python main.py --query "3 days in Paris, budget 120 euros" --agents itinerary food transport

  sk_185786f03f917b5617c5b559d8cb365cbcdf592e196faed0
"""

import argparse
import sys
from llm import get_llm
from schema import TravelPlan
from utils import extract_json, pretty_print_plan, save_plan_to_file


AGENTS = {
    "stays":      {"label": "Stay finder",       "icon": "🏨", "task": "find_stays"},
    "itinerary":  {"label": "Day-by-day plan",   "icon": "🗺️ ", "task": "plan_itinerary"},
    "food":       {"label": "Food & dining",     "icon": "🍽️ ", "task": "recommend_food"},
    "tips":       {"label": "Travel tips",       "icon": "⚡", "task": "travel_tips"},
    "transport":  {"label": "Transport options", "icon": "🚇", "task": "transport_options"},
    "weather":    {"label": "Weather & packing", "icon": "☀️ ", "task": "weather_info"},
    "narrator":   {"label": "Audio guide script","icon": "🎧", "task": "narrator_script"},
}

BRAIN_PROMPT = """
You are the Brain of a multi-agent travel planning system.

Extract these fields from the user query:
- destination (string)
- days (integer)
- budget (integer, per day per person in euros)
- persons (integer, default 1)
- interests (list of strings)
- tasks (leave as empty list — will be overridden)

Rules:
- Default persons to 1 if not specified
- Return STRICT JSON only — no explanation, no markdown, no extra text

Example output:
{
  "destination": "Rome",
  "days": 2,
  "budget": 100,
  "persons": 1,
  "interests": ["history", "food"],
  "tasks": []
}
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Travel Planner — choose which agents to run"
    )
    parser.add_argument("--query", "-q", type=str, default=None)
    parser.add_argument(
        "--agents", "-a",
        nargs="+",
        choices=list(AGENTS.keys()),
        default=None,
        help=f"Agents to run: {', '.join(AGENTS.keys())}"
    )
    parser.add_argument("--save", "-s", action="store_true")
    return parser.parse_args()


def print_menu():
    print("\n" + "=" * 55)
    print("  TRAVEL PLANNER — Agent Selector")
    print("=" * 55)
    for i, (key, info) in enumerate(AGENTS.items(), 1):
        print(f"  [{i}] {info['icon']} {info['label']:<22}  ({key})")
    print("  [8]  Run ALL agents")
    print("  [0]  Cancel")
    print("=" * 55)


def select_agents_interactive() -> list[str]:
    print_menu()
    raw = input("\nEnter numbers (e.g. 1 3 4) or agent names (e.g. itinerary food): ").strip()

    if not raw or raw == "0":
        print("Cancelled.")
        sys.exit(0)

    if raw == "8":
        return list(AGENTS.keys())

    keys = list(AGENTS.keys())
    selected = []

    for token in raw.split():
        token = token.lower().strip(",")
        if token.isdigit():
            idx = int(token) - 1
            if 0 <= idx < len(keys):
                selected.append(keys[idx])
            else:
                print(f"  ⚠️  Ignored unknown number: {token}")
        elif token in AGENTS:
            selected.append(token)
        else:
            print(f"  ⚠️  Ignored unknown agent: '{token}'")

    # Always keep narrator last if selected
    if "narrator" in selected:
        selected = [a for a in selected if a != "narrator"] + ["narrator"]

    return list(dict.fromkeys(selected))  # deduplicate, preserve order


def get_query(args) -> str:
    if args.query:
        return args.query

    print("\nExamples:")
    print('  "2 days in Rome, budget 100 euros, love history and food"')
    print('  "4 days in Tokyo, 2 people, budget 150 euros, anime + ramen"')
    query = input("\nEnter your travel query: ").strip()
    if not query:
        print("No query entered. Exiting.")
        sys.exit(1)
    return query


def parse_plan(query: str) -> TravelPlan:
    llm = get_llm()
    prompt = f"{BRAIN_PROMPT}\n\nUser: {query}"
    response = llm.invoke(prompt)
    data = extract_json(response)
    data["tasks"] = []  # will be injected below
    return TravelPlan(**data)


def run_selected_agents(plan: TravelPlan, agent_keys: list[str]) -> dict:
    from executor import AGENT_REGISTRY

    llm = get_llm()
    results = {}

    print(f"\n{'='*55}")
    print(f"  Running {len(agent_keys)} agent(s)")
    print(f"{'='*55}")

    for key in agent_keys:
        task = AGENTS[key]["task"]
        icon = AGENTS[key]["icon"]
        label = AGENTS[key]["label"]

        if task not in AGENT_REGISTRY:
            print(f"  ⚠️  No agent registered for task '{task}'")
            continue

        AgentClass = AGENT_REGISTRY[task]
        agent = AgentClass(llm=llm)

        print(f"\n  {icon} Running: {label} ...")

        try:
            if task == "narrator_script":
                result = agent.run(plan, context=results)
            else:
                result = agent.run(plan)

            results[task] = result
            print(f"  ✅ Done ({len(result)} chars)")

        except Exception as e:
            results[task] = f"[{label} failed: {e}]"
            print(f"  ❌ Error: {e}")

    return results


def main():
    args = parse_args()

    query = get_query(args)

    print("\n🧠 Parsing your query ...")
    plan = parse_plan(query)

    print(f"\n  Destination : {plan.destination}")
    print(f"  Days        : {plan.days}")
    print(f"  Budget      : €{plan.budget}/day/person")
    print(f"  Persons     : {plan.persons}")
    print(f"  Interests   : {', '.join(plan.interests) or 'general'}")

    # Determine which agents to run
    if args.agents:
        agent_keys = args.agents
        if "narrator" in agent_keys:
            agent_keys = [a for a in agent_keys if a != "narrator"] + ["narrator"]
        print(f"\n  Agents selected via flag: {', '.join(agent_keys)}")
    else:
        agent_keys = select_agents_interactive()

    if not agent_keys:
        print("\nNo agents selected. Exiting.")
        sys.exit(0)

    print(f"\n  Will run: {', '.join(agent_keys)}")
    confirm = input("  Proceed? [Y/n]: ").strip().lower()
    if confirm == "n":
        print("Cancelled.")
        sys.exit(0)

    # Inject selected tasks into plan for compatibility
    plan.tasks = [AGENTS[k]["task"] for k in agent_keys]

    results = run_selected_agents(plan, agent_keys)

    print(f"\n{'='*55}")
    print("  RESULTS")
    print(f"{'='*55}")
    pretty_print_plan(results)

    if args.save:
        save_plan_to_file(plan, results)

    print(f"\n Done! Ran {len(results)}/{len(agent_keys)} agents successfully.")


if __name__ == "__main__":
    main()