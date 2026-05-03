from typing import Any

from agentrex.state.schema import (
    Paper,
    ResearchState,
    STATUS_ERROR,
    STATUS_SUMMARIZING,
)
from agentrex.tools.mcp_client import search_papers


def _coerce_authors(raw_authors: Any) -> list[str]:
    if not isinstance(raw_authors, list):
        return []
    authors: list[str] = []
    for author in raw_authors:
        if isinstance(author, str):
            authors.append(author)
        elif isinstance(author, dict):
            name = author.get("name")
            if isinstance(name, str) and name.strip():
                authors.append(name)
    return authors


def _paper_id_from_record(record: dict[str, Any]) -> str:
    for key in ("paper_id", "id", "arxiv_id"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    for key in ("entry_id", "url", "pdf_url"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            candidate = value.rstrip("/").split("/")[-1]
            if candidate:
                return candidate

    return "unknown"


def _normalize_paper_record(record: dict[str, Any]) -> Paper:
    paper_id = _paper_id_from_record(record)
    title = str(record.get("title", "Untitled")).strip() or "Untitled"
    published = str(record.get("published", record.get("updated", ""))).strip()
    url = str(
        record.get("url", record.get("entry_id", record.get("pdf_url", "")))
    ).strip()
    categories = record.get("categories")
    if not isinstance(categories, list):
        categories = []
    normalized_categories = [str(category) for category in categories if category]

    citation_count = record.get("citation_count")
    if citation_count is not None:
        try:
            citation_count = int(citation_count)
        except (TypeError, ValueError):
            citation_count = None

    return Paper(
        paper_id=paper_id,
        title=title,
        authors=_coerce_authors(record.get("authors")),
        published=published,
        url=url,
        categories=normalized_categories,
        citation_count=citation_count,
    )


def run_fetcher(state: ResearchState) -> ResearchState:
    updated_state = dict(state)
    updated_state["current_agent"] = "fetcher"
    errors = list(updated_state.get("errors", []))

    try:
        paper_records = search_papers(
            query=updated_state["query"],
            max_results=updated_state["paper_count"],
        )
        papers = [_normalize_paper_record(record) for record in paper_records]

        if not papers:
            errors.append("Fetcher error: no papers returned from arXiv MCP search.")
            updated_state["papers"] = []
            updated_state["errors"] = errors
            updated_state["status"] = STATUS_ERROR
            return updated_state

        updated_state["papers"] = papers
        updated_state["errors"] = errors
        updated_state["status"] = STATUS_SUMMARIZING
    except Exception as exc:
        errors.append(f"Fetcher error: {exc}")
        updated_state["papers"] = []
        updated_state["errors"] = errors
        updated_state["status"] = STATUS_ERROR

    return updated_state
