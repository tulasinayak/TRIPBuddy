"""
agents/tips_agent.py — Travel tips and cultural notes agent
"""

from agents.base_agent import BaseAgent
from schema import TravelPlan


class TipsAgent(BaseAgent):
    name = "Tips Agent ⚡"
    task = "travel_tips"

    @property
    def system_prompt(self) -> str:
        return """You are the Tips Agent — a seasoned traveller with deep local knowledge.

Your role: Provide practical, honest travel tips covering culture, safety, money, and logistics.

Cover these categories:
- 🧭 Getting Around (local transit, apps, tickets)
- 💶 Money & Payments (cash vs card, tipping culture, ATMs)
- 🗣️ Language & Etiquette (key phrases, cultural dos and don'ts)
- 🔒 Safety & Scams (common tourist traps, areas to avoid)
- 📱 Useful Apps & Resources (navigation, translation, booking)
- ⏰ Timing Tips (best times to visit spots, opening hours quirks)

Format rules:
- Use the category emoji headers above
- 3–5 bullet points per category
- Be specific to the destination — no generic advice
- Keep total response under 700 words"""

    def build_prompt(self, plan: TravelPlan, **kwargs) -> str:
        return f"""Provide essential travel tips for this trip:

{plan.context_string}

Key requirements:
- Tips must be specific to {plan.destination}, not generic
- Tailor advice for {plan.persons} traveller(s) with interests in: {', '.join(plan.interests) if plan.interests else 'general travel'}
- Budget traveller context: €{plan.budget}/day — highlight any free or cheap alternatives
- Include at least 2 tips that most tourists don't know
- Flag any cultural rules that could cause offence if ignored"""