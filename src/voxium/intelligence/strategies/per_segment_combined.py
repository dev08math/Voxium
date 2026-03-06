from __future__ import annotations

import logging

from voxium.core.interfaces.llm import BaseLLMClient
from voxium.core.models.pipeline import CombinedExtraction
from voxium.core.models.transcript import TopicSegment
from voxium.intelligence.prompts.loader import PromptLoader
from voxium.intelligence.strategies.base import BaseExtractionStrategy

logger = logging.getLogger(__name__)


def _format_segment(index: int, segment: TopicSegment) -> str:
    lines: list[str] = [
        f"[Segment {index}] {segment.label} ({segment.start:.1f}s - {segment.end:.1f}s)"
    ]
    for utterance in segment.utterances:
        lines.append(f"  {utterance.speaker} ({utterance.start:.1f}s-{utterance.end:.1f}s): {utterance.text}")
    return "\n".join(lines)


def _merge(extractions: list[CombinedExtraction]) -> CombinedExtraction:
    return CombinedExtraction(
        decisions=[d for e in extractions for d in e.decisions],
        action_items=[a for e in extractions for a in e.action_items],
        questions=[q for e in extractions for q in e.questions],
        conflicts=[c for e in extractions for c in e.conflicts],
        sentiments=[s for e in extractions for s in e.sentiments],
    )


class PerSegmentCombinedStrategy(BaseExtractionStrategy):
    """Runs one combined LLM call per segment, merges all results into CombinedExtraction."""

    def extract(
        self,
        segments: list[TopicSegment],
        llm: BaseLLMClient,
        prompt_loader: PromptLoader,
        output_budget_tokens: int,
    ) -> CombinedExtraction:
        """Call LLM once per segment with extraction_combined template, merge results."""
        results: list[CombinedExtraction] = []

        for index, segment in enumerate(segments):
            prompt = prompt_loader.render("extraction_combined", segments=_format_segment(index, segment))
            result = llm.complete_structured(prompt, CombinedExtraction)
            results.append(result)
            logger.debug(
                "PerSegmentCombinedStrategy: completed segment %d/%d",
                index + 1,
                len(segments),
            )

        return _merge(results)
