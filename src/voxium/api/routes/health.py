from fastapi import APIRouter, Request

from voxium.api.deps import get_context

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> dict[str, object]:
    """Health check endpoint."""
    ctx = get_context(request)
    return {
        "status": "ok",
        "app": ctx.settings.app_name,
        "debug": ctx.settings.debug,
    }
