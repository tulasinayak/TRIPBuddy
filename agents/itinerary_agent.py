"""
agents/itinerary_agent.py — Day-by-day itinerary planning agent
"""

from agents.base_agent import BaseAgent
from schema import TravelPlan


class ItineraryAgent(BaseAgent):
    name = "Itinerary Agent 🗺️"
    task = "plan_itinerary"

    @property
    def system_prompt(self) -> str:
        return """You are the Itinerary Agent — an expert travel planner who creates detailed, realistic day-by-day itineraries.

Your role: Build a practical, enjoyable itinerary that matches the traveler's interests, budget, and pace.

For each day include:
- Morning, Afternoon, and Evening blocks
- Specific attraction or activity names (real places)
- Estimated time at each location
- Approximate cost in euros (entry fees, etc.)
- Short walking or transit notes between locations
- 1 "hidden gem" tip per day

Format rules:
- Use clear DAY 1, DAY 2 headings
- Use Morning / Afternoon / Evening sub-sections
- Keep each activity description to 2–3 sentences
- End each day with a total estimated spend for activities
- Keep total response under 900 words"""

    def build_prompt(self, plan: TravelPlan, **kwargs) -> str:
        return f"""Create a detailed day-by-day itinerary for this trip:

{plan.context_string}

Key requirements:
- Build exactly {plan.days} day(s) of activities
- Prioritise interests: {', '.join(plan.interests) if plan.interests else 'general sightseeing'}
- Daily activity budget (excluding accommodation): approx €{int(plan.budget * 0.5)}/person
- Group nearby attractions together to minimise travel time
- Include at least one free or low-cost activity per day
- Suggest the best time of day to visit crowded spots"""