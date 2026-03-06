from __future__ import annotations

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

logger = logging.getLogger(__name__)

_DEFAULT_TEMPLATES_DIR = Path(__file__).parent / "templates"


class PromptLoader:
    """Loads and renders Jinja2 prompt templates from the templates directory."""

    def __init__(self, templates_dir: Path = _DEFAULT_TEMPLATES_DIR) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            keep_trailing_newline=True,
        )

    def render(self, template_name: str, **kwargs: object) -> str:
        """Render a prompt template by name with the provided variables."""
        try:
            template = self._env.get_template(f"{template_name}.j2")
        except TemplateNotFound:
            logger.warning("Prompt template not found: %s.j2", template_name)
            raise
        return template.render(**kwargs)

    def exists(self, template_name: str) -> bool:
        """Return True if a template with the given name exists."""
        try:
            self._env.get_template(f"{template_name}.j2")
            return True
        except TemplateNotFound:
            logger.warning("Prompt template not found: %s.j2", template_name)
            return False
