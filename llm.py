"""
llm.py — LLM factory
Supports Ollama (local) and OpenAI. Configure via environment variables.

Usage:
  TRAVEL_LLM=ollama   → uses Ollama with OLLAMA_MODEL (default: mistral)
  TRAVEL_LLM=openai   → uses OpenAI with OPENAI_MODEL (default: gpt-4o-mini)
  TRAVEL_LLM=anthropic → uses Anthropic Claude (default: claude-haiku-4-5-20251001)
"""

import os
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    def invoke(self, prompt: str) -> str: ...


class OllamaClient:
    def __init__(self, model: str = "mistral"):
        from langchain_ollama import OllamaLLM
        self._llm = OllamaLLM(model=model)
        self.model = model
        print(f"  Using Ollama — model: {model}")

    def invoke(self, prompt: str) -> str:
        return self._llm.invoke(prompt)


class OpenAIClient:
    def __init__(self, model: str = "gpt-4o-mini"):
        from openai import OpenAI
        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = model
        print(f"  Using OpenAI — model: {model}")

    def invoke(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content


class AnthropicClient:
    def __init__(self, model: str = "claude-haiku-4-5-20251001"):
        import anthropic
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = model
        print(f"  Using Anthropic — model: {model}")

    def invoke(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


def get_llm() -> LLMClient:
    provider = os.environ.get("TRAVEL_LLM", "ollama").lower()

    print(f"\n🔧 LLM Provider: {provider}")

    if provider == "ollama":
        model = os.environ.get("OLLAMA_MODEL", "mistral")
        return OllamaClient(model=model)
    elif provider == "openai":
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        return OpenAIClient(model=model)
    elif provider == "anthropic":
        model = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
        return AnthropicClient(model=model)
    else:
        raise ValueError(
            f"Unknown LLM provider: '{provider}'. "
            f"Set TRAVEL_LLM to 'ollama', 'openai', or 'anthropic'."
        )