from __future__ import annotations

import logging

from pydantic import BaseModel, Field, RootModel

from voxium.config.settings import VoxiumSettings
from voxium.core.models.pipeline import MeetingMetadata
from voxium.core.models.transcript import TopicSegment, Utterance
from voxium.intelligence.prompts.loader import PromptLoader
from voxium.intelligence.state import MeetingState
from voxium.intelligence.strategies.selector import ExtractionStrategySelector

logger = logging.getLogger(__name__)

_settings = VoxiumSettings()
_prompt_loader = PromptLoader()
_strategy_selector = ExtractionStrategySelector(_settings)


class SegmentShell(BaseModel):
    """LLM response shape for a segment — no utterances, timestamps only."""

    label: str = Field(description="Topic label for this segment")
    start: float = Field(description="Segment start time in seconds")
    end: float = Field(description="Segment end time in seconds")
    summary: str | None = Field(default=None, description="Brief summary of the segment")


def _assign_utterances(
    shells: list[SegmentShell],
    utterances: list[Utterance],
) -> list[TopicSegment]:
    """Map transcript utterances back onto LLM-produced segment shells by timestamp."""
    segments: list[TopicSegment] = []
    for shell in shells:
        matching = [
            u for u in utterances
            if u.start >= shell.start and u.start <= shell.end
        ]
        segments.append(
            TopicSegment(
                label=shell.label,
                start=shell.start,
                end=shell.end,
                summary=shell.summary,
                utterances=matching,
            )
        )
    return segments


def _format_transcript(state: MeetingState) -> str:
    lines: list[str] = []
    for utterance in state["transcript"].utterances:
            lines.append(f"[{utterance.start:.1f}s] {utterance.speaker}: {utterance.text}")
    return "\n".join(lines)


def segment_transcript(state: MeetingState) -> dict:
    """Segment the transcript into labeled topic segments and compute meeting metadata."""
    transcript = state["transcript"]
    llm = state["llm_router"].get("segmentation")

    prompt = _prompt_loader.render("segmentation", transcript=_format_transcript(state))

    ShellList = RootModel[list[SegmentShell]]
    result = llm.complete_structured(prompt, ShellList)
    segments = _assign_utterances(result.root, transcript.utterances)

    utterances = transcript.utterances
    duration_seconds = int(utterances[-1].end - utterances[0].start) if utterances else 0
    total_words = sum(len(u.text.split()) for u in utterances)
    transcript_token_count = int(total_words * 1.3)
    unique_speakers = {u.speaker for u in utterances}

    metadata = MeetingMetadata(
        duration_seconds=duration_seconds,
        segment_count=len(segments),
        transcript_token_count=transcript_token_count,
        speaker_count=len(unique_speakers),
    )

    strategy = _strategy_selector.select(metadata)

    logger.info(
        "Segmentation complete | segments=%d | tokens=%d | strategy=%s",
        len(segments),
        transcript_token_count,
        type(strategy).__name__,
    )
    for seg in segments:
        logger.debug(
            "Segment | label=%r | start=%.2f | end=%.2f | speaker_turns=%d",
            seg.label,
            seg.start,
            seg.end,
            len(seg.utterances),
        )

    return {
        "segments": segments,
        "meeting_metadata": metadata,
        "extraction_strategy": strategy,
        "pipeline_status": {**state.get("pipeline_status", {}), "segmentation": "complete"},
    }
