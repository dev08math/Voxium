import logging
import threading
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from voxium.api.deps import get_context
from voxium.config.context import AppContext

logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)

meetings: dict[str, dict] = {}


class UploadResponse(BaseModel):
    """Response for a successful file upload."""

    meeting_id: str = Field(description="Unique identifier for the uploaded meeting")


class StatusResponse(BaseModel):
    """Response for meeting processing status."""

    status: str = Field(description="Current processing status")
    error: str | None = Field(default=None, description="Error message if processing failed")


def _run_pipeline(meeting_id: str, audio_path: str, ctx: AppContext) -> None:
    """Transcribe audio then invoke the intelligence graph in a background thread."""
    try:
        logger.info("Starting transcription for meeting %s", meeting_id)
        transcript = ctx.transcription_service.transcribe(audio_path)
        logger.info("Transcription complete for meeting %s", meeting_id)

        initial_state = {
            "transcript": transcript,
            "llm_router": ctx.llm_router,
            "pipeline_status": {},
            "iteration": 0,
        }

        logger.info("Invoking intelligence graph for meeting %s", meeting_id)
        final_state = ctx.graph.invoke(initial_state)

        meetings[meeting_id].update({
            "status": "complete",
            "language": transcript.language,
            "duration": transcript.duration,
            "segments": [s.model_dump() for s in final_state.get("segments", [])],
            "decisions": [d.model_dump() for d in final_state.get("decisions", [])],
            "action_items": [a.model_dump() for a in final_state.get("action_items", [])],
            "questions": [q.model_dump() for q in final_state.get("questions", [])],
            "conflicts": [c.model_dump() for c in final_state.get("conflicts", [])],
            "sentiments": [s.model_dump() for s in final_state.get("sentiments", [])],
            "pipeline_status": final_state.get("pipeline_status", {}),
        })
        logger.info("Pipeline complete for meeting %s", meeting_id)

    except Exception as exc:
        logger.exception("Pipeline failed for meeting %s", meeting_id)
        meetings[meeting_id]["status"] = "error"
        meetings[meeting_id]["error"] = str(exc)

    finally:
        path = Path(audio_path)
        if path.exists():
            path.unlink()
            logger.info("Deleted audio file: %s", audio_path)


@router.post("/api/upload")
async def upload_audio(
    file: UploadFile,
    ctx: AppContext = Depends(get_context),
) -> UploadResponse:
    """Upload an audio file for processing."""
    meeting_id = uuid.uuid4().hex[:8]
    ext = Path(file.filename).suffix if file.filename else ".wav"
    save_path = Path(ctx.settings.upload_dir) / f"{meeting_id}{ext}"

    content = await file.read()
    save_path.write_bytes(content)

    meetings[meeting_id] = {
        "status": "uploaded",
        "audio_path": str(save_path),
        "error": None,
    }

    logger.info("Uploaded meeting %s to %s", meeting_id, save_path)
    return UploadResponse(meeting_id=meeting_id)


@router.post("/api/meeting/{meeting_id}/analyze")
async def analyze_meeting(
    meeting_id: str,
    ctx: AppContext = Depends(get_context),
) -> StatusResponse:
    """Start transcription and intelligence pipeline for an uploaded meeting."""
    if meeting_id not in meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting = meetings[meeting_id]
    if meeting["status"] not in ("uploaded", "error"):
        raise HTTPException(
            status_code=400,
            detail=f"Meeting cannot be analyzed in status '{meeting['status']}'",
        )

    meeting["status"] = "processing"
    meeting["error"] = None

    thread = threading.Thread(
        target=_run_pipeline,
        args=(meeting_id, meeting["audio_path"], ctx),
        daemon=True,
    )
    thread.start()

    return StatusResponse(status="processing")


@router.get("/api/meeting/{meeting_id}/status")
async def meeting_status(meeting_id: str) -> StatusResponse:
    """Get the current processing status of a meeting."""
    if meeting_id not in meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting = meetings[meeting_id]
    return StatusResponse(status=meeting["status"], error=meeting.get("error"))


@router.get("/api/meeting/{meeting_id}")
async def get_meeting(meeting_id: str) -> dict:
    """Get full meeting intelligence results. Returns 202 if still processing."""
    if meeting_id not in meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting = meetings[meeting_id]
    if meeting["status"] != "complete":
        raise HTTPException(status_code=202, detail="Meeting still processing")

    return {
        "meeting_id": meeting_id,
        "status": meeting["status"],
        "language": meeting.get("language"),
        "duration": meeting.get("duration"),
        "segments": meeting.get("segments", []),
        "decisions": meeting.get("decisions", []),
        "action_items": meeting.get("action_items", []),
        "questions": meeting.get("questions", []),
        "conflicts": meeting.get("conflicts", []),
        "sentiments": meeting.get("sentiments", []),
        "pipeline_status": meeting.get("pipeline_status", {}),
    }


@router.get("/meeting/{meeting_id}", response_class=HTMLResponse)
async def meeting_page(request: Request, meeting_id: str) -> HTMLResponse:
    """Render the meeting viewer page."""
    if meeting_id not in meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return templates.TemplateResponse(
        request=request,
        name="meeting.html",
        context={"meeting_id": meeting_id},
    )
