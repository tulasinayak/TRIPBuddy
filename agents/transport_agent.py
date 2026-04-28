"""
agents/transport_agent.py — Transport and getting around agent
"""

from agents.base_agent import BaseAgent
from schema import TravelPlan


class TransportAgent(BaseAgent):
    name = "Transport Agent 🚇"
    task = "transport_options"

    @property
    def system_prompt(self) -> str:
        return """You are the Transport Agent — a logistics expert who knows every city's transit system inside out.

Your role: Explain how to get around efficiently and cheaply.

Cover these areas:
- Airport / Station → City Centre (arrival options, cost, time)
- Local Transit (metro, bus, tram — passes, prices, tips)
- Day Trips (if relevant — train/bus options to nearby spots)
- Walking & Cycling (walkability, bike rental, key districts)
- Ride-hailing & Taxis (recommended apps, typical fares, scam warnings)

Format rules:
- Use clear section headers for each transport type
- Always include price estimates in euros
- Compare 2–3 options where available (price vs speed vs convenience)
- Mention any passes or cards worth buying for the trip length
- Keep total response under 600 words"""

    def build_prompt(self, plan: TravelPlan, **kwargs) -> str:
        return f"""Provide transport options and getting-around advice for this trip:

{plan.context_string}

Key requirements:
- Focus on {plan.destination} specifically
- Trip is {plan.days} day(s) — recommend passes or options that make sense for this duration
- Budget-conscious traveller: €{plan.budget}/day total — transport should ideally be under €{int(plan.budget * 0.15)}/day
- Include the most convenient airport/station transfer option
- Flag any transport apps that are essential for this city"""