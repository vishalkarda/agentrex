# AgentRex

Minimal starter for the AgentRex multi-agent platform using:
- FastAPI
- `src` package layout (`src/agentrex`)
- LangGraph workflow skeleton
- FastMCP arXiv server over HTTP (manual run)

## Project Layout

```text
agentrex/
├── src/agentrex/
│   ├── agents/
│   ├── api/endpoints.py
│   ├── mcp_server/arxiv_server.py
│   ├── state/
│   ├── tools/
│   └── main.py
├── data/
│   ├── papers/
│   └── reports/
├── Dockerfile
├── compose.yaml
└── pyproject.toml
```

## Prerequisites

- Python 3.11+
- `uv` installed
- OrbStack running (optional for container workflow)

## Run Locally (uv)

1. Install dependencies:

```bash
uv sync
```

2. Start FastMCP arXiv server (terminal 1):

```bash
uv run python -m agentrex.mcp_server.arxiv_server
```

3. Start API server (terminal 2):

```bash
uv run uvicorn agentrex.main:app --host 0.0.0.0 --port 8000 --reload
```

4. Open:
- Swagger UI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### MCP Environment Variables (optional)

The API connects to the MCP server via HTTP:

- `AGENTREX_ARXIV_MCP_URL` (default: `http://127.0.0.1:8001/mcp`)
- `AGENTREX_ARXIV_MCP_TRANSPORT` (default: `streamable_http`, optional `sse`)

## Run With OrbStack (Docker Compose)

1. Build and start:

```bash
docker compose up --build
```

2. Open:
- Swagger UI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

3. Stop:

```bash
docker compose down
```

## Test Current Endpoints

### Root Endpoint

```bash
curl -s http://localhost:8000/
```

Expected response:

```json
{"message":"AgentRex API is running"}
```

### Health Endpoint

```bash
curl -s http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### Analyze Endpoint

```bash
curl -s -X POST http://localhost:8000/research/analyze \
  -H "Content-Type: application/json" \
  -d '{"query":"attention mechanisms in transformers","paper_count":3}'
```

Expected response shape:

```json
{
  "status": "complete",
  "message": "Analysis workflow completed.",
  "query": "attention mechanisms in transformers",
  "paper_count": 3,
  "report_path": "data/reports/<file>.md",
  "report_file": "<file>.md",
  "errors": []
}
```

### Download Report

```bash
curl -OJ http://localhost:8000/research/download/<report_file>
```

## Notes

- MCP is now network-based (manual FastMCP server), not stdio.
- If MCP server is unavailable, `/research/analyze` returns `status: "error"` with details in `errors`.
