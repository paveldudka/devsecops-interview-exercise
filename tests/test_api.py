"""Integration-style tests at the ASGI boundary."""

import httpx
import pytest

from content_fetcher.api import create_app
from content_fetcher.service import FetchService
from tests.fakes import ScriptedTransport, public_destination_policy, response


@pytest.mark.asyncio
async def test_fetch_endpoint_returns_modeled_content() -> None:
    transport = ScriptedTransport(
        {"https://public.example/readme": response(body=b"document")}
    )
    app = create_app(FetchService(transport, public_destination_policy()))

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        api_response = await client.post(
            "/v1/fetch", json={"url": "https://public.example/readme"}
        )

    assert api_response.status_code == 200
    assert api_response.json() == {
        "requested_url": "https://public.example/readme",
        "final_url": "https://public.example/readme",
        "content_type": None,
        "content": "document",
        "bytes_read": 8,
    }


@pytest.mark.asyncio
async def test_fetch_endpoint_maps_invalid_input_to_client_error() -> None:
    transport = ScriptedTransport({})
    app = create_app(FetchService(transport, public_destination_policy()))

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        api_response = await client.post(
            "/v1/fetch", json={"url": "ftp://public.example/file"}
        )

    assert api_response.status_code == 422
    assert transport.requests == []


@pytest.mark.asyncio
async def test_fetch_endpoint_maps_upstream_failure_to_bad_gateway() -> None:
    app = create_app(
        FetchService(
            ScriptedTransport(
                {"https://public.example/down": response(status_code=503)}
            ),
            public_destination_policy(),
        )
    )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        api_response = await client.post(
            "/v1/fetch", json={"url": "https://public.example/down"}
        )

    assert api_response.status_code == 502
    assert api_response.json()["detail"] == "upstream fetch failed"
