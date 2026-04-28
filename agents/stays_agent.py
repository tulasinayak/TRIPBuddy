"""
agents/stays_agent.py — Accommodation recommendation agent
"""

from agents.base_agent import BaseAgent
from schema import TravelPlan


class StaysAgent(BaseAgent):
    name = "Stay Agent 🏨"
    task = "find_stays"

    @property
    def system_prompt(self) -> str:
        return """You are the Stay Agent — an expert in finding accommodation.

Your role: Recommend 3–5 specific accommodation options that match the traveler's budget and interests.

For each option include:
- Name (real or realistic-sounding property)
- Type (hostel / guesthouse / hotel / apartment / boutique)
- Approximate price per night in euros
- Neighbourhood / location benefit
- 2–3 key pros
- Any relevant note (e.g. breakfast included, great views, party hostel, quiet)

Format each option clearly. Be specific — name real neighbourhoods. Prices must be realistic for the destination.
Keep total response under 600 words."""

    def build_prompt(self, plan: TravelPlan, **kwargs) -> str:
        return f"""Find accommodation options for this trip:

{plan.context_string}

Budget note: The traveller has €{plan.budget}/day for ALL expenses (accommodation + food + activities).
Accommodation should ideally be €{int(plan.budget * 0.4)}–€{int(plan.budget * 0.6)}/night.

Suggest options from budget to mid-range. Include at least one hostel/guesthouse option if budget allows.
For {plan.persons} person(s) travelling together, note if any options are better suited for groups."""