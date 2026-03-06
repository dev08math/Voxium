from __future__ import annotations

from abc import ABC, abstractmethod

from voxium.core.interfaces.llm import BaseLLMClient
from voxium.core.models.pipeline import CombinedExtraction
from voxium.core.models.transcript import TopicSegment
from voxium.intelligence.prompts.loader import PromptLoader


class BaseExtractionStrategy(ABC):
    """Interface for extraction strategies that run all extraction types in one pass."""

    @abstractmethod
    def extract(
        self,
        segments: list[TopicSegment],
        llm: BaseLLMClient,
        prompt_loader: PromptLoader,
        output_budget_tokens: int,
    ) -> CombinedExtraction:
        """Extract all intelligence from segments and return a combined result."""
