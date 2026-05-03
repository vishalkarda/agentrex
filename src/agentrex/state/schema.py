from dataclasses import dataclass, field
from typing import TypedDict

STATUS_PENDING = "pending"
STATUS_SUMMARIZING = "summarizing"
STATUS_COMPARING = "comparing"
STATUS_GENERATING_REPORT = "generating_report"
STATUS_COMPLETE = "complete"
STATUS_ERROR = "error"


@dataclass(slots=True)
class Paper:
    paper_id: str
    title: str
    authors: list[str]
    published: str
    url: str
    categories: list[str] = field(default_factory=list)
    citation_count: int | None = None


class ResearchState(TypedDict):
    query: str
    paper_count: int
    papers: list[Paper]
    summaries: dict[str, str]
    comparison: str
    report_path: str
    current_agent: str
    status: str
    errors: list[str]


def build_initial_state(query: str, paper_count: int) -> ResearchState:
    return {
        "query": query,
        "paper_count": paper_count,
        "papers": [],
        "summaries": {},
        "comparison": "",
        "report_path": "",
        "current_agent": "supervisor",
        "status": STATUS_PENDING,
        "errors": [],
    }
