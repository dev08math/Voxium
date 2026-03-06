from langgraph.graph.state import CompiledStateGraph

from voxium.config.settings import VoxiumSettings
from voxium.core.interfaces.llm import BaseLLMClient
from voxium.core.interfaces.transcription import BaseTranscriptionService
from voxium.intelligence.graph import build_graph
from voxium.llm.openai_compatible import OpenAICompatibleClient
from voxium.llm.router import LLMRouter
from voxium.transcription.whisperx import WhisperXTranscriptionService


class AppContext:
    """Application context holding shared dependencies."""

    def __init__(
        self,
        settings: VoxiumSettings,
        transcription_service: BaseTranscriptionService,
        llm_router: LLMRouter,
        graph: CompiledStateGraph,
    ) -> None:
        self.settings = settings
        self.transcription_service = transcription_service
        self.llm_router = llm_router
        self.graph = graph


def create_context(settings: VoxiumSettings) -> AppContext:
    """Create application context from settings."""
    transcription_service = WhisperXTranscriptionService(
        model_size=settings.whisper_model,
        compute_type=settings.whisper_compute_type,
        device=settings.whisper_device,
        hf_token=settings.hf_token,
        batch_size=settings.whisper_batch_size,
    )

    gemini_client: BaseLLMClient = OpenAICompatibleClient(
        base_url=settings.gemini_base_url,
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )
    llm_router = LLMRouter(default_client=gemini_client)
    graph = build_graph(llm_router)

    return AppContext(
        settings=settings,
        transcription_service=transcription_service,
        llm_router=llm_router,
        graph=graph,
    )
