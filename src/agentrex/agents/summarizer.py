from agentrex.state.schema import (
    ResearchState,
    STATUS_COMPARING,
)


def run_summarizer(state: ResearchState) -> ResearchState:
    updated_state = dict(state)
    updated_state["current_agent"] = "summarizer"
    updated_state["summaries"] = {}
    updated_state["status"] = STATUS_COMPARING
    return updated_state
