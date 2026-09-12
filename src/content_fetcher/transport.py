"""Outbound HTTP transport boundary."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

import httpx


class TransportError(Exception):
    """The outbound HTTP operation failed."""


@dataclass(frozen=True)
class HttpResponse:
    """Transport-neutral HTTP response with lowercase-normalized header keys."""

    status_code: int
    headers: Mapping[str, str]
    body: bytes

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "headers",
            {key.lower(): value for key, value in self.headers.items()},
        )


class HttpTransport(Protocol):
    """The single-request transport used by the service."""

    async def get(self, url: str) -> HttpResponse:
        """Issue one HTTP GET without automatically following redirects."""
        ...


class HttpxTransport:
    """Production adapter around httpx."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client
        self._owns_client = client is None

    async def get(self, url: str) -> HttpResponse:
        if self._client is None:
            self._client = httpx.AsyncClient(follow_redirects=False)
        try:
            response = await self._client.get(url, follow_redirects=False)
        except httpx.HTTPError as exc:
            raise TransportError("outbound HTTP request failed") from exc
        return HttpResponse(
            status_code=response.status_code,
            headers=response.headers,
            body=response.content,
        )

    async def close(self) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()
