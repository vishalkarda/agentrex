# AgentRex

Minimal starter for the AgentRex multi-agent platform using:
- FastAPI
- `src` package layout (`src/agentrex`)
- Docker/Compose (works with OrbStack)

## Project Layout

```text
agentrex/
├── src/agentrex/
│   ├── api/endpoints.py
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
- OrbStack running (for container workflow)

## Run Locally (uv)

1. Install dependencies:

```bash
uv sync
```

2. Start API server:

```bash
uv run uvicorn agentrex.main:app --host 0.0.0.0 --port 8000 --reload
```

3. Open:
- Swagger UI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

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

## Notes

- Current code is a baseline scaffold.
- Next step is adding `/research/analyze` and LangGraph workflow integration.
