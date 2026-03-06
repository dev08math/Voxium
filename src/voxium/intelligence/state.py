from __future__ import annotations

from typing import TypedDict, Required

from voxium.core.models.extraction import (
    ActionItem,
    Conflict,
    Decision,
    Question,
    SegmentSentiment,
)
from voxium.core.models.pipeline import EvaluationResult, MeetingMetadata
from voxium.core.models.transcript import DiarizedTranscript, TopicSegment
from voxium.intelligence.strategies.base import BaseExtractionStrategy
from voxium.llm.router import LLMRouter

class MeetingState(TypedDict, total=False):
    """LangGraph state for the meeting intelligence pipeline."""

    # Input
    transcript: Required[DiarizedTranscript]

    # Segmentation outputs
    segments: list[TopicSegment]
    meeting_metadata: Required[MeetingMetadata]
    extraction_strategy: Required[BaseExtractionStrategy]

    # Routing
    llm_router: Required[LLMRouter]

    # Extraction outputs
    decisions: list[Decision]
    action_items: list[ActionItem]
    questions: list[Question]
    conflicts: list[Conflict]
    sentiments: list[SegmentSentiment]

    # Evaluation
    evaluation: EvaluationResult
    iteration: int

    # Pipeline bookkeeping
    pipeline_status: dict[str, str]
