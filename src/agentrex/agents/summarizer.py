import re

from agentrex.state.schema import (
    ResearchState,
    STATUS_COMPARING,
    STATUS_ERROR,
)
from agentrex.tools.mcp_client import fetch_pdf_text


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _heuristic_summary(text: str, sentence_count: int = 3) -> str:
    cleaned = _clean_text(text)
    if not cleaned:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    selected = [sentence for sentence in sentences if sentence][:sentence_count]
    summary = " ".join(selected).strip()
    if not summary:
        summary = cleaned[:500]
    return summary[:1000]


def run_summarizer(state: ResearchState) -> ResearchState:
    updated_state = dict(state)
    updated_state["current_agent"] = "summarizer"
    errors = list(updated_state.get("errors", []))
    summaries = dict(updated_state.get("summaries", {}))
    papers = updated_state.get("papers", [])

    if not papers:
        errors.append("Summarizer error: no papers available in state.")
        updated_state["errors"] = errors
        updated_state["status"] = STATUS_ERROR
        return updated_state

    for paper in papers:
        try:
            text = fetch_pdf_text(paper.paper_id)
            summary = _heuristic_summary(text)
            if not summary:
                raise ValueError("empty summary generated")
            summaries[paper.paper_id] = summary
        except Exception as exc:
            errors.append(f"Summarizer error for {paper.paper_id}: {exc}")

    updated_state["summaries"] = summaries
    updated_state["errors"] = errors
    updated_state["status"] = STATUS_COMPARING if summaries else STATUS_ERROR
    return updated_state
