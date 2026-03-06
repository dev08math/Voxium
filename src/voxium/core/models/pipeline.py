from pydantic import BaseModel, Field

from voxium.core.models.extraction import (
    ActionItem,
    Conflict,
    Decision,
    Question,
    SegmentSentiment,
)


class MeetingMetadata(BaseModel):
    """Structural metadata about a meeting derived from its transcript."""

    duration_seconds: int = Field(description="Total meeting duration in seconds")
    segment_count: int = Field(description="Number of topic segments")
    transcript_token_count: int = Field(description="Estimated token count of the full transcript")
    speaker_count: int = Field(description="Number of distinct speakers identified")


class EvaluationResult(BaseModel):
    """Output from the evaluator node after checking extraction completeness."""

    passed: bool = Field(description="Whether the extraction passed quality checks")
    gaps: list[str] = Field(description="Descriptions of gaps or missing extractions found")
    reprocess_agents: list[str] = Field(description="Agent names that should be re-run to fill gaps")
    reprocess_context: str = Field(description="Context hint passed to re-triggered agents")


class CombinedExtraction(BaseModel):
    """All extraction outputs for a meeting, aggregated across all agents."""

    decisions: list[Decision] = Field(description="Decisions made during the meeting")
    action_items: list[ActionItem] = Field(description="Action items assigned during the meeting")
    questions: list[Question] = Field(description="Questions raised during the meeting")
    conflicts: list[Conflict] = Field(description="Conflicts identified during the meeting")
    sentiments: list[SegmentSentiment] = Field(description="Sentiment per topic segment")


class CostBreakdown(BaseModel):
    """Token usage and cost accounting for a single pipeline run."""

    meeting_id: str = Field(description="Identifier of the meeting this breakdown belongs to")
    total_local_tokens: int = Field(description="Total tokens consumed by local LLM calls")
    total_cloud_tokens: int = Field(description="Total tokens consumed by cloud LLM calls")
    estimated_cost_usd: float = Field(description="Estimated total cost in USD")
    per_agent: dict[str, int] = Field(description="Token count per agent name")
