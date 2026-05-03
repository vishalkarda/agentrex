from __future__ import annotations

import os
import re
import time
from typing import Any

import arxiv
import httpx
from mcp.server.fastmcp import FastMCP
from pypdf import PdfReader

SERVER_HOST = os.getenv("AGENTREX_ARXIV_MCP_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("AGENTREX_ARXIV_MCP_PORT", "8001"))
MCP_PATH = os.getenv("AGENTREX_ARXIV_MCP_PATH", "/mcp")
PAPER_CACHE_DIR = os.getenv("AGENTREX_ARXIV_PAPERS_DIR", "data/papers")
MAX_PDF_TEXT_CHARS = int(os.getenv("AGENTREX_ARXIV_MAX_TEXT_CHARS", "50000"))

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


def _normalize_paper_id(paper_id: str) -> str:
    candidate = paper_id.strip()
    if "/abs/" in candidate:
        candidate = candidate.split("/abs/")[-1]
    if "/pdf/" in candidate:
        candidate = candidate.split("/pdf/")[-1]
    return candidate.replace(".pdf", "").strip()


def _paper_filename(paper_id: str) -> str:
    safe_id = re.sub(r"[^A-Za-z0-9._-]", "_", paper_id)
    return f"{safe_id}.pdf"


def _get_single_paper(paper_id: str) -> arxiv.Result:
    normalized_id = _normalize_paper_id(paper_id)
    search = arxiv.Search(id_list=[normalized_id], max_results=1)
    client = arxiv.Client(page_size=1, delay_seconds=1.0, num_retries=3)
    results = list(client.results(search))
    if not results:
        raise ValueError(f"Paper not found for id: {paper_id}")
    return results[0]


def _download_pdf_with_retries(result: arxiv.Result, dirpath: str, filename: str) -> str:
    attempts = 3
    last_error: Exception | None = None
    pdf_url = result.pdf_url
    if not pdf_url:
        raise RuntimeError(f"No PDF URL available for paper_id={result.get_short_id()}")
    destination = os.path.join(dirpath, filename)

    for attempt in range(1, attempts + 1):
        try:
            with httpx.Client(timeout=90.0, follow_redirects=True) as client:
                response = client.get(pdf_url)
                response.raise_for_status()
                content = response.content
            if len(content) < 1024:
                raise RuntimeError(f"Downloaded PDF seems too small ({len(content)} bytes)")
            with open(destination, "wb") as file:
                file.write(content)
            return destination
        except (httpx.HTTPError, OSError, RuntimeError) as exc:
            last_error = exc
            try:
                os.remove(destination)
            except OSError:
                pass
            if attempt < attempts:
                time.sleep(float(attempt))
    raise RuntimeError(f"Failed to download PDF after {attempts} attempts: {last_error}")


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


@mcp.tool()
def get_paper_metadata(paper_id: str) -> dict[str, Any]:
    """Fetch detailed metadata for a single arXiv paper."""
    result = _get_single_paper(paper_id)
    metadata = _paper_to_dict(result)
    metadata["primary_category"] = result.primary_category or ""
    metadata["comment"] = result.comment or ""
    metadata["journal_ref"] = result.journal_ref or ""
    metadata["doi"] = result.doi or ""
    return metadata


@mcp.tool()
def fetch_pdf_text(paper_id: str) -> dict[str, Any]:
    """Download a paper PDF and return extracted text."""
    result = _get_single_paper(paper_id)
    os.makedirs(PAPER_CACHE_DIR, exist_ok=True)

    filename = _paper_filename(result.get_short_id())
    pdf_path = _download_pdf_with_retries(result, PAPER_CACHE_DIR, filename)
    reader = PdfReader(pdf_path)

    chunks: list[str] = []
    total_chars = 0
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if not page_text:
            continue
        remaining = MAX_PDF_TEXT_CHARS - total_chars
        if remaining <= 0:
            break
        clipped = page_text[:remaining]
        chunks.append(clipped)
        total_chars += len(clipped)

    text = "\n".join(chunks).strip()
    return {
        "paper_id": result.get_short_id(),
        "pdf_path": pdf_path,
        "text": text,
        "text_length": len(text),
        "truncated": len(text) >= MAX_PDF_TEXT_CHARS,
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
