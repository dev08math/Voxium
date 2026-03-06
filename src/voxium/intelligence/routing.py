from __future__ import annotations

from voxium.intelligence.state import MeetingState

_MAX_ITERATIONS = 2


def route_after_evaluation(state: MeetingState) -> str:
    """Return the next node name based on evaluation result and iteration count.

    Routes back to extractor if evaluation failed and retries remain.
    Routes to output_generator when evaluation passes or retries are exhausted.
    """
    evaluation = state.get("evaluation")
    iteration = state.get("iteration", 0)

    if evaluation is None:
        return "extractor"

    if not evaluation.passed and iteration < _MAX_ITERATIONS:
        return "extractor"

    return "output_generator"
