from agentrex.state.schema import (
    ResearchState,
    STATUS_SUMMARIZING,
)


def run_fetcher(state: ResearchState) -> ResearchState:
    updated_state = dict(state)
    updated_state["current_agent"] = "fetcher"
    updated_state["papers"] = []
    updated_state["status"] = STATUS_SUMMARIZING
    return updated_state
