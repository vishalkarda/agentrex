from datetime import UTC, datetime
from pathlib import Path

from agentrex.state.schema import (
    ResearchState,
    STATUS_COMPLETE,
)


def _render_report_markdown(state: ResearchState, generated_at: str) -> str:
    papers_section = "No papers were processed yet."
    if state["papers"]:
        paper_lines: list[str] = []
        for index, paper in enumerate(state["papers"], start=1):
            paper_lines.extend(
                [
                    f"### {index}. {paper.title}",
                    f"- Paper ID: {paper.paper_id}",
                    f"- Authors: {', '.join(paper.authors) if paper.authors else 'N/A'}",
                    f"- Published: {paper.published}",
                    f"- URL: {paper.url}",
                    "",
                ]
            )
        papers_section = "\n".join(paper_lines).strip()

    summaries_section = "No summaries generated yet."
    if state["summaries"]:
        summary_lines = []
        for paper_id, summary in state["summaries"].items():
            summary_lines.extend([f"### {paper_id}", summary, ""])
        summaries_section = "\n".join(summary_lines).strip()

    comparison_text = state["comparison"] or "No comparative analysis generated yet."

    return (
        "# Research Paper Analysis Report\n\n"
        f"**Query:** {state['query']}\n"
        f"**Requested Paper Count:** {state['paper_count']}\n"
        f"**Generated At (UTC):** {generated_at}\n\n"
        "---\n\n"
        "## Papers\n\n"
        f"{papers_section}\n\n"
        "## Summaries\n\n"
        f"{summaries_section}\n\n"
        "## Comparative Analysis\n\n"
        f"{comparison_text}\n"
    )


def run_reporter(state: ResearchState) -> ResearchState:
    updated_state = dict(state)
    updated_state["current_agent"] = "reporter"
    now = datetime.now(UTC)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    generated_at = now.strftime("%Y-%m-%d %H:%M:%S")
    report_dir = Path("data/reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = f"research_analysis_{timestamp}.md"
    report_path = report_dir / report_file
    report_content = _render_report_markdown(updated_state, generated_at)
    report_path.write_text(report_content, encoding="utf-8")

    updated_state["report_path"] = str(report_path)
    updated_state["status"] = STATUS_COMPLETE
    return updated_state
