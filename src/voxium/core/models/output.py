from pydantic import BaseModel, Field

from voxium.core.models.extraction import (
    ActionItem,
    Conflict,
    Decision,
    Question,
    SegmentSentiment,
)


class ExecutiveBrief(BaseModel):
    """High-level summary of the meeting."""

    summary: str = Field(description="Executive summary of the meeting")


class DetailedMinutes(BaseModel):
    """Full meeting minutes."""

    content: str = Field(description="Detailed meeting minutes content")


class ActionItemsReport(BaseModel):
    """Collection of action items extracted from the meeting."""

    items: list[ActionItem] = Field(description="List of action items")


class FollowUpEmail(BaseModel):
    """Generated follow-up email for meeting attendees."""

    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")


class MeetingIntelligence(BaseModel):
    """Complete intelligence output for a meeting."""

    meeting_id: str = Field(description="Unique identifier for the meeting")
    executive_brief: ExecutiveBrief | None = Field(
        default=None, description="Executive summary"
    )
    detailed_minutes: DetailedMinutes | None = Field(
        default=None, description="Full meeting minutes"
    )
    action_items: ActionItemsReport | None = Field(
        default=None, description="Extracted action items"
    )
    follow_up_email: FollowUpEmail | None = Field(
        default=None, description="Generated follow-up email"
    )
    decisions: list[Decision] = Field(
        default=[], description="Decisions made during the meeting"
    )
    questions: list[Question] = Field(
        default=[], description="Questions raised during the meeting"
    )
    conflicts: list[Conflict] = Field(
        default=[], description="Conflicts or disagreements identified"
    )
    sentiments: list[SegmentSentiment] = Field(
        default=[], description="Sentiment analysis per segment"
    )
