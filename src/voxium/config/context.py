from voxium.config.settings import VoxiumSettings
from voxium.core.interfaces.transcription import BaseTranscriptionService
from voxium.transcription.whisperx import WhisperXTranscriptionService


class AppContext:
    """Application context holding shared dependencies."""

    def __init__(
        self,
        settings: VoxiumSettings,
        transcription_service: BaseTranscriptionService,
    ) -> None:
        self.settings = settings
        self.transcription_service = transcription_service


def create_context(settings: VoxiumSettings) -> AppContext:
    """Create application context from settings."""
    transcription_service = WhisperXTranscriptionService(
        model_size=settings.whisper_model,
        compute_type=settings.whisper_compute_type,
        device=settings.whisper_device,
        hf_token=settings.hf_token,
        batch_size=settings.whisper_batch_size,
    )
    return AppContext(settings=settings, transcription_service=transcription_service)
