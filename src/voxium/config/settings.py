from pydantic_settings import BaseSettings


class VoxiumSettings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = {
        "env_prefix": "VOXIUM_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }
    
    app_name: str = "Voxium"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    upload_dir: str = "./voxium_data"
    hf_token: str = ""
    whisper_model: str = "large-v2"
    whisper_compute_type: str = "int8_float16"
    whisper_device: str = "cuda"
    whisper_batch_size: int = 16

    # Primary LLM (Gemini via OpenAI-compatible endpoint)
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    gemini_model: str = "gemini-2.5-flash"

    # Local LLM (Ollama)
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen2.5:7b"

    # Routing
    use_cloud_synthesis: bool = True

    # Strategy
    model_context_window: int = 32000
    output_budget_decisions: int = 1000
    output_budget_action_items: int = 800
    output_budget_questions: int = 900
    output_budget_conflicts: int = 1500
    output_budget_sentiment: int = 600
