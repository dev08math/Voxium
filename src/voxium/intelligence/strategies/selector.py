from __future__ import annotations

from voxium.config.settings import VoxiumSettings
from voxium.core.models.pipeline import MeetingMetadata
from voxium.intelligence.strategies.base import BaseExtractionStrategy
from voxium.intelligence.strategies.dynamic_batch import DynamicBatchStrategy
from voxium.intelligence.strategies.per_segment_combined import PerSegmentCombinedStrategy
from voxium.intelligence.strategies.single_batch import SingleBatchStrategy

_SINGLE_BATCH_THRESHOLD = 8_000
_DYNAMIC_BATCH_THRESHOLD = 20_000


class ExtractionStrategySelector:
    """Selects an extraction strategy based on transcript size."""

    def __init__(self, settings: VoxiumSettings) -> None:
        self._settings = settings

    def select(self, metadata: MeetingMetadata) -> BaseExtractionStrategy:
        """Return the appropriate strategy for the given meeting metadata."""
        token_count = metadata.transcript_token_count

        if token_count < _SINGLE_BATCH_THRESHOLD:
            return SingleBatchStrategy()

        if token_count < _DYNAMIC_BATCH_THRESHOLD:
            return DynamicBatchStrategy(
                model_context_window=self._settings.model_context_window,
                tokens_per_word=1.3,
            )

        return PerSegmentCombinedStrategy()
