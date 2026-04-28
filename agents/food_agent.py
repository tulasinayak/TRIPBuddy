"""
agents/food_agent.py — Food and dining recommendation agent
"""

from agents.base_agent import BaseAgent
from schema import TravelPlan


class FoodAgent(BaseAgent):
    name = "Food Agent 🍽️"
    task = "recommend_food"

    @property
    def system_prompt(self) -> str:
        return """You are the Food Agent — a local food expert and culinary guide.

Your role: Recommend authentic, budget-appropriate dining options covering all meals.

For each recommendation include:
- Restaurant or market name (real or realistic)
- Type of cuisine / dish to try
- Approximate cost per person in euros
- Neighbourhood / location
- Best time to visit or insider tip
- At least one "eat like a local" tip per meal type

Format rules:
- Organise by Breakfast / Lunch / Dinner / Snacks & Street Food
- Include 2–3 options per meal category
- Mark budget-friendly picks with 💰 and splurge picks with ✨
- Keep total response under 700 words"""

    def build_prompt(self, plan: TravelPlan, **kwargs) -> str:
        food_budget = int(plan.budget * 0.35)
        return f"""Recommend food and dining options for this trip:

{plan.context_string}

Key requirements:
- Daily food budget: approx €{food_budget}/person/day (total over {plan.days} days: €{food_budget * plan.days})
- Interests that may affect food style: {', '.join(plan.interests) if plan.interests else 'no specific preferences'}
- Include a mix of sit-down restaurants, street food, and local markets
- Must-try local dishes or drinks for {plan.destination}
- At least one vegetarian-friendly option per meal category
- Avoid tourist traps — focus on where locals actually eat"""