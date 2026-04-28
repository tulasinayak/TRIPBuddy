"""
schema.py — Pydantic models for structured data validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


VALID_TASKS = {
    "find_stays",
    "plan_itinerary",
    "recommend_food",
    "travel_tips",
    "transport_options",
    "weather_info",
    "narrator_script",
}


class TravelPlan(BaseModel):
    destination: str = Field(..., description="City or country to travel to")
    days: int = Field(..., ge=1, le=30, description="Number of days (1–30)")
    budget: int = Field(..., ge=0, description="Daily budget per person in euros")
    persons: int = Field(default=1, ge=1, description="Number of travelers")
    interests: List[str] = Field(default_factory=list, description="List of interests")
    tasks: List[str] = Field(default_factory=list, description="Agent tasks to run")

    @field_validator("tasks")
    @classmethod
    def validate_tasks(cls, v):
        # Always ensure core tasks are present
        core = {"find_stays", "plan_itinerary", "travel_tips"}
        task_set = set(v) | core
        # Filter to only valid tasks
        return [t for t in list(task_set) if t in VALID_TASKS]

    @field_validator("destination")
    @classmethod
    def validate_destination(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Destination must be at least 2 characters")
        return v.strip().title()

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, v):
        return [i.strip().lower() for i in v if i.strip()]

    @property
    def total_budget(self) -> int:
        return self.budget * self.days * self.persons

    @property
    def context_string(self) -> str:
        return (
            f"Destination: {self.destination}, "
            f"{self.days} days, "
            f"€{self.budget}/day/person, "
            f"{self.persons} person(s), "
            f"interests: {', '.join(self.interests) if self.interests else 'general'}, "
            f"total budget: €{self.total_budget}"
        )


class AgentResult(BaseModel):
    agent: str
    task: str
    success: bool
    content: str
    error: Optional[str] = None


class TravelPlanResult(BaseModel):
    plan: TravelPlan
    results: List[AgentResult]

    def get(self, task: str) -> Optional[AgentResult]:
        for r in self.results:
            if r.task == task:
                return r
        return None