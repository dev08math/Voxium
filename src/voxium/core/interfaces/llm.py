from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from voxium.core.exceptions import LLMParseError

T = TypeVar("T", bound=BaseModel)


class BaseLLMClient(ABC):
    """Interface for LLM clients."""

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Send a prompt and return the raw text response."""

    def complete_structured(self, prompt: str, output_model: type[T], max_retries: int = 2) -> T:
        """Send a prompt and parse the response into a Pydantic model.

        Prepends a JSON-only instruction to the prompt, then calls complete().
        Retries up to max_retries times on ValidationError, feeding the error
        back into the prompt. Raises LLMParseError after all retries are exhausted.
        """
        json_prompt = (
            "Respond ONLY with valid JSON that matches the required schema. "
            "Do not include any explanation, markdown formatting, or text outside the JSON object.\n\n"
            + prompt
        )

        last_error: ValidationError | None = None
        for attempt in range(max_retries + 1):
            if attempt > 0 and last_error is not None:
                json_prompt = (
                    json_prompt
                    + f"\n\nYour previous response failed validation with this error:\n{last_error}\n"
                    "Fix the JSON and try again."
                )

            raw = self.complete(json_prompt)

            try:
                return output_model.model_validate_json(raw)
            except ValidationError as exc:
                last_error = exc

        raise LLMParseError(
            f"Failed to parse LLM response into {output_model.__name__} "
            f"after {max_retries + 1} attempts. Last error: {last_error}"
        )
