class VoxiumError(Exception):
    """Base exception for all Voxium errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class TranscriptionError(VoxiumError):
    """Error during audio transcription."""
