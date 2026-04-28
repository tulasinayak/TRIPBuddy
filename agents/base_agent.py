"""
agents/base_agent.py — Abstract base class for all travel agents
"""

from abc import ABC, abstractmethod
from schema import TravelPlan
from typing import Any


class BaseAgent(ABC):
    name: str = "Base Agent"
    task: str = ""

    def __init__(self, llm):
        self.llm = llm

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Each agent defines its own system prompt / persona."""
        ...

    @abstractmethod
    def build_prompt(self, plan: TravelPlan, **kwargs) -> str:
        """Build the full prompt for this agent from the travel plan."""
        ...

    def run(self, plan: TravelPlan, **kwargs) -> str:
        """Execute the agent: build prompt → call LLM → return result."""
        prompt = self.build_prompt(plan, **kwargs)
        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        return self.llm.invoke(full_prompt)