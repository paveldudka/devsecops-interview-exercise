"""Outbound HTTP transport boundary."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

import httpx


@dataclass(frozen=True)
class HttpResponse:
    """Transport-neutral HTTP response."""

    status_code: int
    headers: Mapping[str, str]
    body: bytes


class HttpTransport(Protocol):
    """The single-request transport used by the service."""

    async def get(self, url: str) -> HttpResponse:
        """Issue one HTTP GET without automatically following redirects."""
        ...


class HttpxTransport:
    """Production adapter around httpx."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(follow_redirects=False)

    async def get(self, url: str) -> HttpResponse:
        response = await self._client.get(url)
        return HttpResponse(
            status_code=response.status_code,
            headers=response.headers,
            body=response.content,
        )

    async def close(self) -> None:
        await self._client.aclose()
