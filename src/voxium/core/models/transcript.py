from pydantic import BaseModel, Field


class Utterance(BaseModel):
    """A single speaker utterance within a transcript."""

    speaker: str = Field(description="Speaker identifier or name")
    text: str = Field(description="Transcribed text content")
    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")
    confidence: float | None = Field(default=None, description="Transcription confidence score")


class DiarizedTranscript(BaseModel):
    """Complete transcript with speaker diarization."""

    utterances: list[Utterance] = Field(description="Ordered list of speaker utterances")
    language: str = Field(description="Detected language code")
    duration: float | None = Field(default=None, description="Total audio duration in seconds")


class TopicSegment(BaseModel):
    """A segment of the transcript grouped by topic."""

    label: str = Field(description="Topic label for this segment")
    start: float = Field(description="Segment start time in seconds")
    end: float = Field(description="Segment end time in seconds")
    utterances: list[Utterance] = Field(description="Utterances within this segment")
    summary: str | None = Field(default=None, description="Brief summary of the segment")
