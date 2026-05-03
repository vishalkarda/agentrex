from agentrex.state.schema import (
    ResearchState,
    STATUS_GENERATING_REPORT,
)


def run_comparator(state: ResearchState) -> ResearchState:
    updated_state = dict(state)
    updated_state["current_agent"] = "comparator"
    updated_state["comparison"] = (
        "Comparator stub: comparative analysis will be generated in a later increment."
    )
    updated_state["status"] = STATUS_GENERATING_REPORT
    return updated_state
