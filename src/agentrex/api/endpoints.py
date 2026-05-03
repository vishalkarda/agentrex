from anyio import to_thread
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel, Field
from uuid import uuid4

from agentrex.agents.supervisor import get_research_graph
from agentrex.state.schema import (
    ResearchState,
    STATUS_ERROR,
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
    report_file: str
    errors: list[str] = Field(default_factory=list)


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
        message=(
            "Analysis workflow completed."
            if final_state["status"] != STATUS_ERROR
            else "Analysis workflow failed."
        ),
        query=final_state["query"],
        paper_count=final_state["paper_count"],
        report_path=final_state["report_path"],
        report_file=Path(final_state["report_path"]).name,
        errors=final_state.get("errors", []),
    )


@router.get("/research/download/{filename}", tags=["research"])
async def download_report(filename: str) -> FileResponse:
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    report_dir = Path("data/reports")
    report_path = report_dir / filename

    if report_path.name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    if not report_path.exists() or not report_path.is_file():
        raise HTTPException(status_code=404, detail="Report not found.")

    return FileResponse(
        path=report_path,
        media_type="text/markdown",
        filename=filename,
    )
