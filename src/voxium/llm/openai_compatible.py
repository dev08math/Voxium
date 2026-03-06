from __future__ import annotations

import logging
import time

import openai

from voxium.core.exceptions import LLMCallError
from voxium.core.interfaces.llm import BaseLLMClient

logger = logging.getLogger(__name__)


class OpenAICompatibleClient(BaseLLMClient):
    """LLM client for any OpenAI-compatible endpoint (Gemini, OpenAI, Ollama, etc.)."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> None:
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = openai.OpenAI(base_url=base_url, api_key=api_key)

    def complete(self, prompt: str) -> str:
        """Send a single user message and return the response text."""
        start = time.monotonic()
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
        except openai.OpenAIError as exc:
            raise LLMCallError(f"LLM API call failed: {exc}") from exc

        duration = time.monotonic() - start
        usage = response.usage
        logger.info(
            "LLM call complete | model=%s prompt_tokens=%s completion_tokens=%s duration=%.2fs",
            self._model,
            usage.prompt_tokens if usage else "?",
            usage.completion_tokens if usage else "?",
            duration,
        )

        content = response.choices[0].message.content
        if content is None:
            raise LLMCallError("LLM returned an empty response.")
        return content
