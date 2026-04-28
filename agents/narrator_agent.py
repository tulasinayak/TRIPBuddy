"""
agents/narrator_agent.py — Audio guide script narrator agent (optional)
Converts the itinerary into an engaging, story-driven audio guide script.
"""

from agents.base_agent import BaseAgent
from schema import TravelPlan


class NarratorAgent(BaseAgent):
    name = "Narrator Agent 🎧"
    task = "narrator_script"

    @property
    def system_prompt(self) -> str:
        return """You are the Narrator Agent — a world-class travel documentary scriptwriter and audio guide author.

Your role: Transform the travel itinerary into a vivid, engaging audio guide script that a traveller can listen to while exploring.

Script style:
- Warm, conversational tone — like a knowledgeable friend guiding you
- Rich with historical anecdotes, sensory descriptions, and local stories
- Direct second-person address: "As you turn the corner, you'll see..."
- Each location gets a mini-story or fascinating fact
- Natural audio cues: pauses, "look to your left", "take a moment to..."

Format rules:
- Open with a dramatic welcome to the destination
- One section per major attraction or area
- Use [PAUSE] markers for natural breathing moments
- Use [LOOK: direction/thing] for spatial guidance
- End with a reflective closing that captures the spirit of the place
- Target 600–800 words (approx 4–5 minutes of audio at natural speaking pace)"""

    def build_prompt(self, plan: TravelPlan, **kwargs) -> str:
        context = kwargs.get("context", {})

        itinerary_summary = ""
        if "plan_itinerary" in context:
            itinerary_summary = f"\n\nITINERARY TO BASE SCRIPT ON:\n{context['plan_itinerary'][:1200]}"

        tips_summary = ""
        if "travel_tips" in context:
            tips_summary = f"\n\nLOCAL INSIGHTS TO WEAVE IN:\n{context['travel_tips'][:400]}"

        return f"""Write an audio guide script for this trip:

{plan.context_string}
{itinerary_summary}
{tips_summary}

Key requirements:
- Focus on {plan.destination}'s highlights relevant to: {', '.join(plan.interests) if plan.interests else 'general culture and history'}
- Script should feel cinematic and personal, not like a Wikipedia article
- Weave in at least 2 surprising historical facts or local legends
- Include sensory details: sounds, smells, textures the traveller will experience
- Make the listener feel excited and present, not like they're in a lecture"""