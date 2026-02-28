from abc import ABC, abstractmethod

from voxium.core.models.transcript import DiarizedTranscript


class BaseTranscriptionService(ABC):
    """Interface for transcription services."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> DiarizedTranscript:
        """Transcribe an audio file and return a diarized transcript."""
