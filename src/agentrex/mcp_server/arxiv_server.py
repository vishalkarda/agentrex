from __future__ import annotations

import os
from typing import Any

import arxiv
from mcp.server.fastmcp import FastMCP

SERVER_HOST = os.getenv("AGENTREX_ARXIV_MCP_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("AGENTREX_ARXIV_MCP_PORT", "8001"))
MCP_PATH = os.getenv("AGENTREX_ARXIV_MCP_PATH", "/mcp")

mcp = FastMCP(
    name="agentrex-arxiv-mcp",
    instructions="MCP tools for searching arXiv papers used by AgentRex.",
    host=SERVER_HOST,
    port=SERVER_PORT,
    streamable_http_path=MCP_PATH,
)


def _paper_to_dict(result: arxiv.Result) -> dict[str, Any]:
    return {
        "paper_id": result.get_short_id(),
        "title": result.title,
        "authors": [author.name for author in result.authors],
        "published": result.published.isoformat() if result.published else "",
        "updated": result.updated.isoformat() if result.updated else "",
        "url": result.entry_id or "",
        "pdf_url": result.pdf_url or "",
        "categories": list(result.categories or []),
        "summary": result.summary or "",
    }


@mcp.tool()
def search_papers(query: str, max_results: int = 3) -> list[dict[str, Any]]:
    """Search arXiv papers and return normalized metadata records."""
    capped_results = max(1, min(max_results, 20))
    search = arxiv.Search(
        query=query,
        max_results=capped_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    client = arxiv.Client(page_size=capped_results, delay_seconds=1.0, num_retries=3)
    return [_paper_to_dict(result) for result in client.results(search)]


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
