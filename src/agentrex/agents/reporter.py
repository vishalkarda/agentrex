from datetime import UTC, datetime

from agentrex.state.schema import (
    ResearchState,
    STATUS_COMPLETE,
)


def run_reporter(state: ResearchState) -> ResearchState:
    updated_state = dict(state)
    updated_state["current_agent"] = "reporter"
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    updated_state["report_path"] = f"data/reports/research_analysis_{timestamp}.md"
    updated_state["status"] = STATUS_COMPLETE
    return updated_state
