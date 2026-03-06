from __future__ import annotations

import logging
import math

from voxium.core.interfaces.llm import BaseLLMClient
from voxium.core.models.pipeline import CombinedExtraction
from voxium.core.models.transcript import TopicSegment
from voxium.intelligence.prompts.loader import PromptLoader
from voxium.intelligence.strategies.base import BaseExtractionStrategy

logger = logging.getLogger(__name__)

_SYSTEM_OVERHEAD_TOKENS = 500
_MIN_BATCH_SIZE = 1
_MAX_BATCH_SIZE = 10


def _format_segments(segments: list[TopicSegment]) -> str:
    lines: list[str] = []
    for index, segment in enumerate(segments):
        lines.append(f"[Segment {index}] {segment.label} ({segment.start:.1f}s - {segment.end:.1f}s)")
        for utterance in segment.utterances:
            lines.append(f"  {utterance.speaker} ({utterance.start:.1f}s-{utterance.end:.1f}s): {utterance.text}")
        lines.append("")
    return "\n".join(lines).strip()


def _count_words(segments: list[TopicSegment]) -> int:
    return sum(
        len(utterance.text.split())
        for segment in segments
        for utterance in segment.utterances
    )


def _merge(extractions: list[CombinedExtraction]) -> CombinedExtraction:
    return CombinedExtraction(
        decisions=[d for e in extractions for d in e.decisions],
        action_items=[a for e in extractions for a in e.action_items],
        questions=[q for e in extractions for q in e.questions],
        conflicts=[c for e in extractions for c in e.conflicts],
        sentiments=[s for e in extractions for s in e.sentiments],
    )


class DynamicBatchStrategy(BaseExtractionStrategy):
    """Splits segments into context-window-aware batches, merges CombinedExtraction results."""

    def __init__(self, model_context_window: int, tokens_per_word: float = 1.3) -> None:
        self._model_context_window = model_context_window
        self._tokens_per_word = tokens_per_word

    def _compute_batch_size(self, segments: list[TopicSegment], output_budget_tokens: int) -> int:
        total_segment_tokens = _count_words(segments) * self._tokens_per_word
        per_segment_token_cost = total_segment_tokens / len(segments)
        available_input_tokens = self._model_context_window - output_budget_tokens - _SYSTEM_OVERHEAD_TOKENS
        return int(max(min(math.floor(available_input_tokens / per_segment_token_cost), _MAX_BATCH_SIZE), _MIN_BATCH_SIZE))

    def extract(
        self,
        segments: list[TopicSegment],
        llm: BaseLLMClient,
        prompt_loader: PromptLoader,
        output_budget_tokens: int,
    ) -> CombinedExtraction:
        """Split segments into batches, call LLM per batch, merge into single CombinedExtraction."""
        batch_size = self._compute_batch_size(segments, output_budget_tokens)
        batches = [segments[i : i + batch_size] for i in range(0, len(segments), batch_size)]

        logger.debug(
            "DynamicBatchStrategy: batch_size=%d total_batches=%d",
            batch_size,
            len(batches),
        )

        results: list[CombinedExtraction] = []
        for batch in batches:
            prompt = prompt_loader.render("extraction_combined", segments=_format_segments(batch))
            results.append(llm.complete_structured(prompt, CombinedExtraction))

        return _merge(results)
