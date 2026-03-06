from __future__ import annotations

import logging

from voxium.core.interfaces.llm import BaseLLMClient
from voxium.core.models.pipeline import CombinedExtraction
from voxium.core.models.transcript import TopicSegment
from voxium.intelligence.prompts.loader import PromptLoader
from voxium.intelligence.strategies.base import BaseExtractionStrategy

logger = logging.getLogger(__name__)


def _format_segments(segments: list[TopicSegment]) -> str:
    lines: list[str] = []
    for index, segment in enumerate(segments):
        lines.append(f"[Segment {index}] {segment.label} ({segment.start:.1f}s - {segment.end:.1f}s)")
        for utterance in segment.utterances:
            lines.append(f"  {utterance.speaker} ({utterance.start:.1f}s-{utterance.end:.1f}s): {utterance.text}")
        lines.append("")
    return "\n".join(lines).strip()


class SingleBatchStrategy(BaseExtractionStrategy):
    """Sends all segments in a single LLM call and returns CombinedExtraction."""

    def extract(
        self,
        segments: list[TopicSegment],
        llm: BaseLLMClient,
        prompt_loader: PromptLoader,
        output_budget_tokens: int,
    ) -> CombinedExtraction:
        """Render prompt with all segments, call LLM once, return parsed CombinedExtraction."""
        prompt = prompt_loader.render("extraction_combined", segments=_format_segments(segments))
        return llm.complete_structured(prompt, CombinedExtraction)
