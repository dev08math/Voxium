from pydantic import BaseModel, Field


class Decision(BaseModel):
    """A decision made during the meeting."""

    description: str = Field(description="What was decided")
    made_by: str | None = Field(default=None, description="Who made or announced the decision")
    segment_index: int | None = Field(default=None, description="Index of the topic segment where this occurred")
    confidence: float | None = Field(default=None, description="Extraction confidence score")


class ActionItem(BaseModel):
    """A task or action item assigned during the meeting."""

    description: str = Field(description="What needs to be done")
    assignee: str | None = Field(default=None, description="Person responsible for this action")
    deadline: str | None = Field(default=None, description="Due date or timeframe if mentioned")
    priority: str | None = Field(default=None, description="Priority level if mentioned")
    segment_index: int | None = Field(default=None, description="Index of the topic segment where this occurred")


class Question(BaseModel):
    """A question raised during the meeting."""

    text: str = Field(description="The question that was asked")
    asked_by: str | None = Field(default=None, description="Who asked the question")
    answered: bool = Field(default=False, description="Whether the question was answered in the meeting")
    answer_summary: str | None = Field(default=None, description="Brief summary of the answer if provided")
    answered_by: str | None = Field(default=None, description="Who answered the question")


class Conflict(BaseModel):
    """A disagreement or conflicting viewpoint between speakers."""

    speaker_a_statement: str = Field(description="First speaker's position")
    speaker_b_statement: str = Field(description="Second speaker's position")
    speaker_a: str = Field(description="First speaker identifier")
    speaker_b: str = Field(description="Second speaker identifier")
    topic: str | None = Field(default=None, description="Topic of the disagreement")
    severity: str | None = Field(default=None, description="Severity level of the conflict")


class SegmentSentiment(BaseModel):
    """Sentiment analysis for a topic segment."""

    segment_index: int = Field(description="Index of the topic segment")
    tone: str = Field(description="Overall tone of the segment")
    speakers_sentiment: dict[str, str] | None = Field(
        default=None, description="Per-speaker sentiment within the segment"
    )
