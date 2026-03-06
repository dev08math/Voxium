from __future__ import annotations

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from voxium.intelligence.nodes.extractor import extract_all
from voxium.intelligence.nodes.segmentation import segment_transcript
from voxium.intelligence.state import MeetingState
from voxium.llm.router import LLMRouter


def _generate_output(state: MeetingState) -> dict:
    """Stub output generator node. Will be replaced with synthesis logic."""
    return {
        "pipeline_status": {**state.get("pipeline_status", {}), "output_generator": "complete"},
    }


def build_graph(llm_router: LLMRouter) -> CompiledStateGraph:
    """Build and compile the meeting intelligence LangGraph pipeline.

    llm_router must be passed in the initial state when calling graph.invoke().
    """
    graph = StateGraph(MeetingState)

    graph.add_node("segmentation", segment_transcript)
    graph.add_node("extractor", extract_all)
    graph.add_node("output_generator", _generate_output)

    graph.set_entry_point("segmentation")

    graph.add_edge("segmentation", "extractor")
    graph.add_edge("extractor", "output_generator")
    graph.add_edge("output_generator", END)

    return graph.compile()
