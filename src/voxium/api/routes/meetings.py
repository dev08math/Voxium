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


def _run_transcription(meeting_id: str, audio_path: str, ctx: AppContext) -> None:
    """Run transcription in a background thread."""
    try:
        logger.info("Starting transcription for meeting %s", meeting_id)
        transcript = ctx.transcription_service.transcribe(audio_path)

        meetings[meeting_id]["utterances"] = [
            u.model_dump() for u in transcript.utterances
        ]
        meetings[meeting_id]["language"] = transcript.language
        meetings[meeting_id]["duration"] = transcript.duration
        meetings[meeting_id]["status"] = "complete"
        logger.info("Transcription complete for meeting %s", meeting_id)

    except Exception as exc:
        logger.exception("Transcription failed for meeting %s", meeting_id)
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
    """Start transcription analysis for an uploaded meeting."""
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
        target=_run_transcription,
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
    """Get full meeting data. Returns 202 if still processing."""
    if meeting_id not in meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting = meetings[meeting_id]
    if meeting["status"] != "complete":
        raise HTTPException(status_code=202, detail="Meeting still processing")

    return {
        "meeting_id": meeting_id,
        "status": meeting["status"],
        "language": meeting.get("language"),
        "segments": meeting.get("utterances", []),
        "duration": meeting.get("duration"),
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
