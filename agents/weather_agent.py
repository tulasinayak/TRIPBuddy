"""
agents/weather_agent.py — Weather and seasonal advice agent
"""

from agents.base_agent import BaseAgent
from schema import TravelPlan
from datetime import datetime


class WeatherAgent(BaseAgent):
    name = "Weather Agent ☀️"
    task = "weather_info"

    @property
    def system_prompt(self) -> str:
        return """You are the Weather Agent — a knowledgeable travel advisor specialising in climate and packing advice.

Your role: Give accurate seasonal weather expectations and practical packing guidance.

Cover these areas:
- 🌡️ Expected Temperature Range (day / night)
- 🌧️ Precipitation & Weather Patterns
- ☀️ Daylight Hours & Best Outdoor Times
- 🧳 Packing List (clothes, gear, essentials)
- ⚠️ Weather Warnings or Seasonal Considerations

Format rules:
- Use the emoji section headers above
- Be specific to the season / month of travel if inferable
- Packing list should be concise bullet points (10–15 items max)
- Flag any weather-related activity timing advice
- Keep total response under 500 words"""

    def build_prompt(self, plan: TravelPlan, **kwargs) -> str:
        current_month = datetime.now().strftime("%B")
        return f"""Provide weather information and packing advice for this trip:

{plan.context_string}

Key requirements:
- Current month is approximately {current_month} — use this for seasonal accuracy
- Destination: {plan.destination}
- Trip length: {plan.days} day(s)
- Include advice on how weather affects the planned interests: {', '.join(plan.interests) if plan.interests else 'general sightseeing'}
- Note if weather could affect any outdoor activities or sightseeing
- Suggest the best time of day for outdoor activities given typical weather patterns"""