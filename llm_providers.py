"""LLM provider integrations with fallback and cost tracking."""

import logging
import time
from typing import Dict, Optional

import tiktoken
from anthropic import Anthropic
from openai import OpenAI

from config import Config

logger = logging.getLogger(__name__)


# Pricing per million tokens.
PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
}


class CostTracker:
    """Track API usage costs across providers."""

    def __init__(self):
        self.total_cost = 0.0
        self.requests = []

    def track_request(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Track one provider request and return its estimated cost."""
        pricing = PRICING.get(model, {"input": 3.00, "output": 15.00})
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        cost = input_cost + output_cost

        self.total_cost += cost
        self.requests.append(
            {
                "provider": provider,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
            }
        )
        return cost

    def get_summary(self) -> Dict:
        """Return aggregate cost and token usage."""
        total_input = sum(request["input_tokens"] for request in self.requests)
        total_output = sum(request["output_tokens"] for request in self.requests)

        return {
            "total_requests": len(self.requests),
            "total_cost": self.total_cost,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "average_cost": self.total_cost / max(len(self.requests), 1),
        }

    def check_budget(self, daily_budget: float):
        """Raise if the estimated daily budget has been exceeded."""
        if self.total_cost >= daily_budget:
            raise RuntimeError(
                f"Daily budget of ${daily_budget:.2f} exceeded. "
                f"Current: ${self.total_cost:.2f}"
            )

        percent_used = (self.total_cost / daily_budget) * 100
        if percent_used >= 90:
            logger.warning("%.1f%% of daily budget used", percent_used)


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count tokens for supported models, falling back to a rough estimate."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        return max(1, len(text) // 4)


class LLMProviders:
    """Manage OpenAI and Anthropic calls with rate limits and fallback."""

    def __init__(
        self,
        openai_client: Optional[OpenAI] = None,
        anthropic_client: Optional[Anthropic] = None,
        cost_tracker: Optional[CostTracker] = None,
    ):
        self.openai_client = openai_client or OpenAI(api_key=Config.OPENAI_API_KEY)
        self.anthropic_client = anthropic_client or Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.cost_tracker = cost_tracker or CostTracker()

        self.openai_last_call = 0.0
        self.anthropic_last_call = 0.0
        self.openai_interval = 60.0 / Config.OPENAI_RPM
        self.anthropic_interval = 60.0 / Config.ANTHROPIC_RPM

    def _wait_openai(self):
        """Apply simple OpenAI rate limiting."""
        elapsed = time.time() - self.openai_last_call
        if elapsed < self.openai_interval:
            time.sleep(self.openai_interval - elapsed)
        self.openai_last_call = time.time()

    def _wait_anthropic(self):
        """Apply simple Anthropic rate limiting."""
        elapsed = time.time() - self.anthropic_last_call
        if elapsed < self.anthropic_interval:
            time.sleep(self.anthropic_interval - elapsed)
        self.anthropic_last_call = time.time()

    def ask_openai(self, prompt: str, model: Optional[str] = None, max_tokens: int = 300) -> str:
        """Send a prompt to OpenAI."""
        model = model or Config.OPENAI_MODEL
        self._wait_openai()

        input_tokens = count_tokens(prompt, model)
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3,
        )

        output_text = response.choices[0].message.content or ""
        output_tokens = count_tokens(output_text, model)
        self.cost_tracker.track_request("openai", model, input_tokens, output_tokens)
        self.cost_tracker.check_budget(Config.DAILY_BUDGET)
        return output_text

    def ask_anthropic(self, prompt: str, model: Optional[str] = None, max_tokens: int = 300) -> str:
        """Send a prompt to Anthropic."""
        model = model or Config.ANTHROPIC_MODEL
        self._wait_anthropic()

        input_tokens = count_tokens(prompt, model)
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        output_text = response.content[0].text if response.content else ""
        output_tokens = count_tokens(output_text, model)
        self.cost_tracker.track_request("anthropic", model, input_tokens, output_tokens)
        self.cost_tracker.check_budget(Config.DAILY_BUDGET)
        return output_text

    def ask_with_fallback(
        self,
        prompt: str,
        primary: str = "openai",
        max_tokens: int = 300,
    ) -> Dict[str, str]:
        """Ask the primary provider and retry with the secondary provider on failure."""
        providers = {
            "openai": self.ask_openai,
            "anthropic": self.ask_anthropic,
        }
        if primary not in providers:
            raise ValueError(f"Unknown provider: {primary}")

        secondary = "anthropic" if primary == "openai" else "openai"
        try:
            response = providers[primary](prompt, max_tokens=max_tokens)
            return {"provider": primary, "response": response}
        except Exception as primary_error:
            logger.warning("%s failed: %s", primary, primary_error)

        try:
            response = providers[secondary](prompt, max_tokens=max_tokens)
            return {"provider": secondary, "response": response}
        except Exception as secondary_error:
            raise RuntimeError("All providers failed") from secondary_error


class OpenAIProvider:
    """Compatibility wrapper for older tests and callers."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        self.providers = LLMProviders(openai_client=OpenAI(api_key=self.api_key))

    def summarize(self, text: str, max_tokens: int = 150) -> Optional[str]:
        """Summarize text using OpenAI."""
        prompt = f"Summarize this article in 2-3 sentences:\n\n{text}"
        return self.providers.ask_openai(prompt, model=self.model, max_tokens=max_tokens)


class AnthropicProvider:
    """Compatibility wrapper for older tests and callers."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        self.model = model or Config.ANTHROPIC_MODEL
        self.providers = LLMProviders(anthropic_client=Anthropic(api_key=self.api_key))

    def summarize(self, text: str, max_tokens: int = 150) -> Optional[str]:
        """Summarize text using Anthropic."""
        prompt = f"Summarize this article in 2-3 sentences:\n\n{text}"
        return self.providers.ask_anthropic(prompt, model=self.model, max_tokens=max_tokens)


class LLMFactory:
    """Factory for compatibility with the earlier implementation."""

    @staticmethod
    def get_provider(provider_name: str = "openai", **kwargs):
        """Return a provider wrapper by name."""
        providers = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
        }

        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            logger.error("Unknown provider: %s", provider_name)
            return None

        return provider_class(**kwargs)


if __name__ == "__main__":
    Config.validate()
    providers = LLMProviders()
    result = providers.ask_with_fallback(
        "What is machine learning? Answer in one sentence.",
        primary="openai",
    )
    print(f"Provider used: {result['provider']}")
    print(result["response"])
    print(providers.cost_tracker.get_summary())
