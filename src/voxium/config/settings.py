from pydantic_settings import BaseSettings


class VoxiumSettings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = {"env_prefix": "VOXIUM_"}

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
