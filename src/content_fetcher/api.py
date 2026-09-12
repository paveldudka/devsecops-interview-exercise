"""FastAPI entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from content_fetcher.models import FetchRequest, FetchResult
from content_fetcher.service import FetchService, InvalidUrlError, UpstreamError
from content_fetcher.transport import HttpxTransport

logger = logging.getLogger(__name__)


def create_app(fetch_service: FetchService | None = None) -> FastAPI:
    """Create the API, optionally with an injected service."""

    owned_transport: HttpxTransport | None = None
    service = fetch_service
    if service is None:
        owned_transport = HttpxTransport()
        service = FetchService(owned_transport)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            if owned_transport is not None:
                await owned_transport.close()

    app = FastAPI(title="Content Fetcher", version="0.1.0", lifespan=lifespan)
    # This also makes injected services available to ASGI test clients, which do
    # not run application lifespan events automatically.
    app.state.fetch_service = service

    @app.get("/healthz")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/fetch", response_model=FetchResult)
    async def fetch(payload: FetchRequest) -> FetchResult:
        try:
            service: FetchService = app.state.fetch_service
            return await service.fetch(payload.url)
        except InvalidUrlError as exc:
            logger.warning("fetch failed url=%r error=%r", payload.url, exc)
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except UpstreamError as exc:
            logger.warning("upstream failed url=%r error=%r", payload.url, exc)
            raise HTTPException(
                status_code=502, detail="upstream fetch failed"
            ) from exc

    return app


app = create_app()
