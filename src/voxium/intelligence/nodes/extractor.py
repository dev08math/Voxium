from __future__ import annotations

import logging

from voxium.config.settings import VoxiumSettings
from voxium.intelligence.prompts.loader import PromptLoader
from voxium.intelligence.state import MeetingState

logger = logging.getLogger(__name__)

_settings = VoxiumSettings()
_prompt_loader = PromptLoader()

_TOTAL_OUTPUT_BUDGET = (
    _settings.output_budget_decisions
    + _settings.output_budget_action_items
    + _settings.output_budget_questions
    + _settings.output_budget_conflicts
    + _settings.output_budget_sentiment
)


def extract_all(state: MeetingState) -> dict:
    """Run the extraction strategy across all segments and return all extraction types."""
    llm = state["llm_router"].get("extractor")
    strategy = state["extraction_strategy"]

    result = strategy.extract(
        segments=state.get("segments", []),
        llm=llm,
        prompt_loader=_prompt_loader,
        output_budget_tokens=_TOTAL_OUTPUT_BUDGET,
    )

    logger.info(
        "Extraction complete | decisions=%d | action_items=%d | questions=%d | conflicts=%d | sentiments=%d",
        len(result.decisions),
        len(result.action_items),
        len(result.questions),
        len(result.conflicts),
        len(result.sentiments),
    )
    logger.debug("decisions=%s", [d.model_dump() for d in result.decisions])
    logger.debug("action_items=%s", [a.model_dump() for a in result.action_items])
    logger.debug("questions=%s", [q.model_dump() for q in result.questions])
    logger.debug("conflicts=%s", [c.model_dump() for c in result.conflicts])
    logger.debug("sentiments=%s", [s.model_dump() for s in result.sentiments])

    return {
        "decisions": result.decisions,
        "action_items": result.action_items,
        "questions": result.questions,
        "conflicts": result.conflicts,
        "sentiments": result.sentiments,
        "pipeline_status": {**state.get("pipeline_status", {}), "extractor": "complete"},
    }
