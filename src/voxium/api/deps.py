from fastapi import Request

from voxium.config.context import AppContext


def get_context(request: Request) -> AppContext:
    """Extract application context from request state."""
    return request.app.state.ctx
