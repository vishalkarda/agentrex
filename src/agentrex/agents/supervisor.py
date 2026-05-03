from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from agentrex.agents.comparator import run_comparator
from agentrex.agents.fetcher import run_fetcher
from agentrex.agents.reporter import run_reporter
from agentrex.agents.summarizer import run_summarizer
from agentrex.state.checkpointer import create_checkpointer
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


def run_supervisor(state: ResearchState) -> ResearchState:
    updated_state = dict(state)
    updated_state["current_agent"] = "supervisor"
    return updated_state


@lru_cache(maxsize=1)
def get_research_graph():
    graph_builder = StateGraph(ResearchState)
    graph_builder.add_node("supervisor", run_supervisor)
    graph_builder.add_node("fetcher", run_fetcher)
    graph_builder.add_node("summarizer", run_summarizer)
    graph_builder.add_node("comparator", run_comparator)
    graph_builder.add_node("reporter", run_reporter)

    graph_builder.add_edge(START, "supervisor")
    graph_builder.add_conditional_edges(
        "supervisor",
        route_next_agent,
        {
            ROUTE_FETCHER: "fetcher",
            ROUTE_SUMMARIZER: "summarizer",
            ROUTE_COMPARATOR: "comparator",
            ROUTE_REPORTER: "reporter",
            ROUTE_END: END,
            ROUTE_ERROR: END,
        },
    )
    graph_builder.add_edge("fetcher", "supervisor")
    graph_builder.add_edge("summarizer", "supervisor")
    graph_builder.add_edge("comparator", "supervisor")
    graph_builder.add_edge("reporter", "supervisor")

    return graph_builder.compile(checkpointer=create_checkpointer())
