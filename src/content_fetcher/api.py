"""FastAPI entry point."""

import logging

from fastapi import FastAPI, HTTPException

from content_fetcher.models import FetchRequest, FetchResult
from content_fetcher.service import FetchError, FetchService
from content_fetcher.transport import HttpxTransport

logger = logging.getLogger(__name__)


def create_app(fetch_service: FetchService | None = None) -> FastAPI:
    """Create the API, optionally with a deterministic transport for tests."""

    app = FastAPI(title="Content Fetcher", version="0.1.0")
    service = fetch_service or FetchService(HttpxTransport())

    @app.get("/healthz")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/fetch", response_model=FetchResult)
    async def fetch(payload: FetchRequest) -> FetchResult:
        try:
            return await service.fetch(payload.url)
        except FetchError as exc:
            logger.warning("fetch failed url=%s error=%s", payload.url, exc)
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return app


app = create_app()
