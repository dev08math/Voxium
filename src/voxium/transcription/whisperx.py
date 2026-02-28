import gc
import logging

import torch
import whisperx
from whisperx.diarize import DiarizationPipeline

from voxium.core.exceptions import TranscriptionError
from voxium.core.interfaces.transcription import BaseTranscriptionService
from voxium.core.models.transcript import DiarizedTranscript, Utterance

logger = logging.getLogger(__name__)


class WhisperXTranscriptionService(BaseTranscriptionService):
    """Transcription service backed by WhisperX with diarization."""

    def __init__(
        self,
        model_size: str,
        compute_type: str,
        device: str,
        hf_token: str,
        batch_size: int = 16,
    ) -> None:
        self._model_size = model_size
        self._compute_type = compute_type
        self._device = device
        self._hf_token = hf_token
        self._batch_size = batch_size

    def _cleanup(self) -> None:
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def transcribe(self, audio_path: str) -> DiarizedTranscript:
        """Transcribe audio file with alignment and optional diarization."""
        try:
            logger.info("Loading whisper model: %s", self._model_size)
            model = whisperx.load_model(
                self._model_size,
                self._device,
                compute_type=self._compute_type,
            )
            audio = whisperx.load_audio(audio_path)
            result = model.transcribe(audio, batch_size=self._batch_size)
            del model
            self._cleanup()

            logger.info("Aligning transcript")
            align_model, metadata = whisperx.load_align_model(
                language_code=result["language"],
                device=self._device,
            )
            result = whisperx.align(
                result["segments"],
                align_model,
                metadata,
                audio,
                self._device,
            )
            del align_model
            self._cleanup()

            if self._hf_token:
                logger.info("Running diarization")
                diarize_model = DiarizationPipeline(
                    token=self._hf_token,
                    device=self._device,
                )
                diarize_segments = diarize_model(audio_path)
                result = whisperx.assign_word_speakers(diarize_segments, result)
                del diarize_model
                self._cleanup()

            utterances = [
                Utterance(
                    speaker=seg.get("speaker", "UNKNOWN"),
                    text=seg["text"].strip(),
                    start=seg["start"],
                    end=seg["end"],
                )
                for seg in result["segments"]
            ]

            language = result.get("language", "en")
            logger.info(
                "Transcription complete: %d utterances, language=%s",
                len(utterances),
                language,
            )

            return DiarizedTranscript(utterances=utterances, language=language)

        except TranscriptionError:
            raise
        except Exception as exc:
            logger.exception("Transcription failed for %s", audio_path)
            raise TranscriptionError(f"Transcription failed: {exc}") from exc
