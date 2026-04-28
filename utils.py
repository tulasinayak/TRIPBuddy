"""
utils.py — Shared utilities: JSON extraction, formatting, file saving
"""

import json
import re
import os
from datetime import datetime
from typing import Any


def extract_json(text: str) -> dict:
    """
    Robustly extracts a JSON object from an LLM response.
    Handles markdown code fences, extra text, trailing commas.
    """
    # Strip markdown code fences
    text = re.sub(r"```(?:json)?", "", text).strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find first {...} block
    match = re.search(r"\{[\s\S]+\}", text)
    if not match:
        raise ValueError(f"No JSON object found in LLM response:\n{text}")

    json_str = match.group()

    # Fix trailing commas (common LLM mistake)
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON from LLM response.\nError: {e}\nText: {json_str}")


def pretty_print_plan(results: dict) -> None:
    """Print the final travel plan in a readable format."""
    sections = {
        "find_stays": ("🏨", "ACCOMMODATION"),
        "plan_itinerary": ("🗺️ ", "ITINERARY"),
        "recommend_food": ("🍽️ ", "FOOD & DINING"),
        "travel_tips": ("⚡", "TRAVEL TIPS"),
        "transport_options": ("🚇", "TRANSPORT"),
        "weather_info": ("☀️ ", "WEATHER"),
        "narrator_script": ("🎧", "AUDIO GUIDE SCRIPT"),
    }

    for task, (icon, label) in sections.items():
        if task in results and results[task]:
            print(f"\n{icon} {label}")
            print("-" * 50)
            content = results[task]
            # Truncate for terminal display
            if len(content) > 800:
                print(content[:800] + "\n... [truncated, see output file]")
            else:
                print(content)


def save_plan_to_file(plan_data: Any, results: dict, output_dir: str = "output") -> str:
    """Save the full travel plan to a markdown file."""
    os.makedirs(output_dir, exist_ok=True)

    destination = getattr(plan_data, "destination", "trip").replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/{destination}_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Travel Plan: {plan_data.destination}\n\n")
        f.write(f"**Duration:** {plan_data.days} days\n")
        f.write(f"**Budget:** €{plan_data.budget}/day/person\n")
        f.write(f"**Travelers:** {plan_data.persons}\n")
        f.write(f"**Interests:** {', '.join(plan_data.interests)}\n")
        f.write(f"**Total Budget:** €{plan_data.total_budget}\n\n")
        f.write("---\n\n")

        section_titles = {
            "find_stays": "🏨 Accommodation",
            "plan_itinerary": "🗺️ Itinerary",
            "recommend_food": "🍽️ Food & Dining",
            "travel_tips": "⚡ Travel Tips",
            "transport_options": "🚇 Transport",
            "weather_info": "☀️ Weather",
            "narrator_script": "🎧 Audio Guide Script",
        }

        for task, title in section_titles.items():
            if task in results and results[task]:
                f.write(f"## {title}\n\n")
                f.write(results[task])
                f.write("\n\n---\n\n")

    print(f"\n💾 Plan saved to: {filename}")
    return filename


def chunk_text_for_tts(text: str, max_chars: int = 500) -> list[str]:
    """Split text into chunks suitable for TTS APIs."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < max_chars:
            current += " " + sentence
        else:
            if current:
                chunks.append(current.strip())
            current = sentence

    if current:
        chunks.append(current.strip())

    return chunks