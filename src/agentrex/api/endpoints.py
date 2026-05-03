from fastapi import APIRouter
from pydantic import BaseModel, Field

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

    return AnalyzeResponse(
        status=initial_state["status"],
        message="Analysis request accepted (stub). Workflow wiring is next.",
        query=initial_state["query"],
        paper_count=initial_state["paper_count"],
    )
