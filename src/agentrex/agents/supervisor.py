from agentrex.state.schema import (
    ResearchState,
    STATUS_COMPARING,
    STATUS_COMPLETE,
    STATUS_ERROR,
    STATUS_GENERATING_REPORT,
    STATUS_PENDING,
    STATUS_SUMMARIZING,
)

ROUTE_FETCHER = "fetcher"
ROUTE_SUMMARIZER = "summarizer"
ROUTE_COMPARATOR = "comparator"
ROUTE_REPORTER = "reporter"
ROUTE_END = "end"
ROUTE_ERROR = "error"

STATUS_TO_ROUTE: dict[str, str] = {
    STATUS_PENDING: ROUTE_FETCHER,
    STATUS_SUMMARIZING: ROUTE_SUMMARIZER,
    STATUS_COMPARING: ROUTE_COMPARATOR,
    STATUS_GENERATING_REPORT: ROUTE_REPORTER,
    STATUS_COMPLETE: ROUTE_END,
    STATUS_ERROR: ROUTE_ERROR,
}


def route_next_agent(state: ResearchState) -> str:
    status = state.get("status", STATUS_ERROR)
    return STATUS_TO_ROUTE.get(status, ROUTE_ERROR)
