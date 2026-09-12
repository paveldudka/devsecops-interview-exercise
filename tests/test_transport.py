"""Offline tests for the production HTTP adapter."""

import httpx
import pytest

from content_fetcher.transport import HttpxTransport, TransportError


@pytest.mark.asyncio
async def test_wraps_httpx_transport_failure_without_network() -> None:
    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("modeled connection failure", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(fail)) as client:
        transport = HttpxTransport(client)

        with pytest.raises(TransportError):
            await transport.get("https://public.example/unavailable")

        await transport.close()
        assert not client.is_closed
