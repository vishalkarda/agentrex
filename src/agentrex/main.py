from fastapi import FastAPI

from agentrex.api.endpoints import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgentRex API",
        version="0.1.0",
        description="Starter API for the AgentRex multi-agent platform.",
    )
    app.include_router(router)
    return app

app = create_app()
