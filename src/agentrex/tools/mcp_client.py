from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient

ARXIV_SERVER_NAME = "arxiv"
SEARCH_TOOL_CANDIDATES = ("search_papers", "arxiv_search")
METADATA_TOOL_CANDIDATES = ("get_paper_metadata", "paper_metadata")
PDF_TEXT_TOOL_CANDIDATES = ("fetch_pdf_text", "read_paper", "download_paper")
SUPPORTED_TRANSPORTS = {"streamable_http", "sse"}


def _resolve_transport() -> str:
    transport = os.getenv("AGENTREX_ARXIV_MCP_TRANSPORT", "streamable_http").strip()
    if transport not in SUPPORTED_TRANSPORTS:
        allowed = ", ".join(sorted(SUPPORTED_TRANSPORTS))
        raise ValueError(f"Unsupported AGENTREX_ARXIV_MCP_TRANSPORT '{transport}'. Use one of: {allowed}.")
    return transport


def _build_mcp_client() -> MultiServerMCPClient:
    transport = _resolve_transport()
    server_url = os.getenv("AGENTREX_ARXIV_MCP_URL", "http://127.0.0.1:8001/mcp").strip()
    connections = {
        ARXIV_SERVER_NAME: {
            "transport": transport,
            "url": server_url,
        }
    }
    return MultiServerMCPClient(connections)


def _decode_json_if_possible(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _extract_records(payload: Any) -> list[dict[str, Any]]:
    payload = _decode_json_if_possible(payload)

    if isinstance(payload, list):
        # FastMCP tools can return content blocks like:
        # [{"type": "text", "text": "{...json...}", "id": "..."}]
        if payload and all(isinstance(item, dict) and "text" in item for item in payload):
            extracted: list[dict[str, Any]] = []
            for block in payload:
                text = block.get("text")
                if isinstance(text, str):
                    extracted.extend(_extract_records(text))
            return extracted
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        for key in ("papers", "results", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [payload]

    if hasattr(payload, "artifact"):
        artifact = _decode_json_if_possible(getattr(payload, "artifact"))
        return _extract_records(artifact)

    if hasattr(payload, "content"):
        content = getattr(payload, "content")
        if isinstance(content, list):
            content_text = " ".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and isinstance(block.get("text"), str)
            )
            return _extract_records(content_text)
        if isinstance(content, str):
            return _extract_records(content)

    return []


async def _search_papers_async(query: str, max_results: int) -> list[dict[str, Any]]:
    result = await _invoke_tool_async(
        SEARCH_TOOL_CANDIDATES,
        {"query": query, "max_results": max_results},
    )
    return _extract_records(result)


async def _get_paper_metadata_async(paper_id: str) -> dict[str, Any]:
    result = await _invoke_tool_async(METADATA_TOOL_CANDIDATES, {"paper_id": paper_id})
    records = _extract_records(result)
    if not records:
        raise RuntimeError(f"No metadata returned for paper_id={paper_id}")
    return records[0]


async def _fetch_pdf_text_async(paper_id: str) -> str:
    result = await _invoke_tool_async(PDF_TEXT_TOOL_CANDIDATES, {"paper_id": paper_id})
    records = _extract_records(result)
    if not records:
        raise RuntimeError(f"No PDF text payload returned for paper_id={paper_id}")
    payload = records[0]
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError(f"Empty PDF text returned for paper_id={paper_id}")
    return text


async def _invoke_tool_async(tool_candidates: tuple[str, ...], payload: dict[str, Any]) -> Any:
    client = _build_mcp_client()
    tools = await client.get_tools(server_name=ARXIV_SERVER_NAME)
    tool_by_name = {tool.name: tool for tool in tools}

    tool = None
    for candidate in tool_candidates:
        if candidate in tool_by_name:
            tool = tool_by_name[candidate]
            break

    if tool is None:
        available = ", ".join(sorted(tool_by_name.keys())) or "<none>"
        expected = ", ".join(tool_candidates)
        raise RuntimeError(
            f"Requested MCP tool not found. Expected one of: {expected}. Available: {available}"
        )

    return await tool.ainvoke(payload)


def search_papers(query: str, max_results: int) -> list[dict[str, Any]]:
    return asyncio.run(_search_papers_async(query=query, max_results=max_results))


def get_paper_metadata(paper_id: str) -> dict[str, Any]:
    return asyncio.run(_get_paper_metadata_async(paper_id=paper_id))


def fetch_pdf_text(paper_id: str) -> str:
    return asyncio.run(_fetch_pdf_text_async(paper_id=paper_id))
