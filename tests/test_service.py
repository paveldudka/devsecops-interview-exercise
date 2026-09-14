"""Product behavior at the service boundary."""

import pytest

from content_fetcher.service import FetchService, InvalidUrlError, UpstreamError
from tests.fakes import ScriptedTransport, response


@pytest.mark.asyncio
async def test_fetches_https_content() -> None:
    transport = ScriptedTransport(
        {
            "https://public.example/article": response(
                headers=(("content-type", "text/plain"),), body=b"hello"
            )
        }
    )

    result = await FetchService(transport).fetch("https://public.example/article")

    assert result.content == "hello"
    assert result.content_type == "text/plain"
    assert result.bytes_read == 5
    assert result.final_url == "https://public.example/article"
    assert transport.requests == ["https://public.example/article"]


@pytest.mark.asyncio
async def test_follows_absolute_and_relative_redirects() -> None:
    transport = ScriptedTransport(
        {
            "http://public.example/start": response(
                302, headers=(("Location", "https://cdn.example/content"),)
            ),
            "https://cdn.example/content": response(
                301, headers=(("location", "/v2/content"),)
            ),
            "https://cdn.example/v2/content": response(body=b"redirected"),
        }
    )

    result = await FetchService(transport).fetch("http://public.example/start")

    assert result.content == "redirected"
    assert result.final_url == "https://cdn.example/v2/content"
    assert transport.requests == [
        "http://public.example/start",
        "https://cdn.example/content",
        "https://cdn.example/v2/content",
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    ["mailto:user@example.com", "data:text/plain,hello", "https:///missing-host"],
)
async def test_rejects_unsupported_url_shapes(url: str) -> None:
    transport = ScriptedTransport({})

    with pytest.raises(InvalidUrlError):
        await FetchService(transport).fetch(url)

    assert transport.requests == []


@pytest.mark.asyncio
async def test_rejects_user_information_without_making_a_request() -> None:
    transport = ScriptedTransport({})

    with pytest.raises(InvalidUrlError):
        await FetchService(transport).fetch(
            "https://user:password@public.example/article"
        )

    assert transport.requests == []


@pytest.mark.asyncio
async def test_rejects_malformed_url() -> None:
    transport = ScriptedTransport({})

    with pytest.raises(InvalidUrlError):
        await FetchService(transport).fetch("http://[invalid")

    assert transport.requests == []


@pytest.mark.asyncio
async def test_surfaces_upstream_failure() -> None:
    transport = ScriptedTransport(
        {"https://public.example/missing": response(status_code=404)}
    )

    with pytest.raises(UpstreamError):
        await FetchService(transport).fetch("https://public.example/missing")


@pytest.mark.asyncio
@pytest.mark.parametrize("location", ["ftp://files.example/item", "http://[bad"])
async def test_maps_invalid_redirect_target_to_upstream_failure(location: str) -> None:
    start = "https://public.example/start"
    transport = ScriptedTransport(
        {start: response(302, headers=(("Location", location),))}
    )

    with pytest.raises(UpstreamError):
        await FetchService(transport).fetch(start)

    assert transport.requests == [start]
