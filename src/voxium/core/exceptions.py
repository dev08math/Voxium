class VoxiumError(Exception):
    """Base exception for all Voxium errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class TranscriptionError(VoxiumError):
    """Error during audio transcription."""


class LLMCallError(VoxiumError):
    """HTTP or API-level failure when calling an LLM provider."""


class LLMParseError(VoxiumError):
    """Failed to parse LLM response into the expected Pydantic model."""
