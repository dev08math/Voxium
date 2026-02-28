# Voxium

Multi-agent meeting intelligence system. Records meeting audio, transcribes with speaker diarization, and runs an agentic analysis pipeline to extract structured intelligence — decisions, action items, questions, conflicts, sentiment.

## Status

**Work in progress.** Scaffolding and data models in place. Transcription and agent pipeline coming next.

## Architecture

```
Audio File
    ↓
[ Transcription ]     WhisperX — speaker-labeled transcript
    ↓
[ Intelligence ]      LangGraph — multi-agent extraction + evaluation loop
    ↓
[ API ]               FastAPI — serves results as JSON + HTML
```

## Stack

- **Transcription:** WhisperX (CTranslate2, int8_float16, pyannote diarization)
- **Orchestration:** LangGraph (state machine, fan-out/fan-in, conditional routing)
- **Local LLM:** Qwen 2.5 7B via Ollama
- **Cloud LLM:** GPT-4o-mini (optional, for synthesis)
- **API:** FastAPI
- **Capture:** Chrome extension (MV3, tabCapture)

## Setup

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/voxium.git
cd voxium

# Install dependencies
uv sync

# Configure
cp .env.example .env
# Edit .env with your tokens

# Run
uv run python -m uvicorn voxium.api.app:app --host 0.0.0.0 --port 8000
```

## License

MIT