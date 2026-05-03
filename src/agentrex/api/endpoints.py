from anyio import to_thread
from fastapi import APIRouter
from pydantic import BaseModel, Field
from uuid import uuid4

from agentrex.agents.supervisor import get_research_graph
from agentrex.state.schema import (
    ResearchState,
    build_initial_state,
)

router = APIRouter()


class AnalyzeRequest(BaseModel):
    query: str = Field(min_length=3, max_length=300)
    paper_count: int = Field(default=3, ge=1, le=10)


class AnalyzeResponse(BaseModel):
    status: str
    message: str
    query: str
    paper_count: int
    report_path: str


@router.get("/", tags=["system"])
async def root() -> dict[str, str]:
    return {"message": "AgentRex API is running"}


@router.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/research/analyze", response_model=AnalyzeResponse, tags=["research"])
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    initial_state: ResearchState = build_initial_state(
        query=request.query,
        paper_count=request.paper_count,
    )
    graph = get_research_graph()
    final_state = await to_thread.run_sync(
        graph.invoke,
        initial_state,
        {"configurable": {"thread_id": str(uuid4())}},
    )

    return AnalyzeResponse(
        status=final_state["status"],
        message="Analysis workflow completed (stub graph).",
        query=final_state["query"],
        paper_count=final_state["paper_count"],
        report_path=final_state["report_path"],
    )
