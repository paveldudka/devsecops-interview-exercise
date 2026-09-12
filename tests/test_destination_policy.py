"""Adversarial tests for the worked destination policy."""

import pytest

from content_fetcher.destination_policy import DestinationPolicy, StaticResolver
from content_fetcher.service import FetchService, InvalidUrlError, UpstreamError
from tests.fakes import ScriptedTransport, response


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/admin",
        "http://[::1]/admin",
        "http://169.254.169.254/latest/data",
        "http://10.20.30.40/internal",
        "http://[fe80::1]/internal",
    ],
)
async def test_denies_non_global_ip_literals_before_transport(url: str) -> None:
    transport = ScriptedTransport({url: response(body=b"sensitive")})
    service = FetchService(transport, DestinationPolicy(StaticResolver({})))

    with pytest.raises(InvalidUrlError, match="not permitted"):
        await service.fetch(url)

    assert transport.requests == []


@pytest.mark.asyncio
async def test_denies_hostname_when_any_answer_is_not_global() -> None:
    url = "https://mixed.example/content"
    transport = ScriptedTransport({url: response(body=b"sensitive")})
    policy = DestinationPolicy(
        StaticResolver({"mixed.example": ("8.8.8.8", "10.0.0.7")})
    )

    with pytest.raises(InvalidUrlError, match="not permitted"):
        await FetchService(transport, policy).fetch(url)

    assert transport.requests == []


@pytest.mark.asyncio
async def test_applies_policy_to_each_redirect_hop() -> None:
    start = "https://public.example/start"
    protected = "http://internal.example/data"
    transport = ScriptedTransport(
        {
            start: response(302, headers=(("Location", protected),)),
            protected: response(body=b"sensitive"),
        }
    )
    policy = DestinationPolicy(
        StaticResolver(
            {"public.example": ("8.8.8.8",), "internal.example": ("10.0.0.7",)}
        )
    )

    with pytest.raises(UpstreamError, match="denied destination"):
        await FetchService(transport, policy).fetch(start)

    assert transport.requests == [start]


@pytest.mark.asyncio
async def test_preserves_public_redirect_chain() -> None:
    start = "https://public.example/start"
    middle = "https://cdn.example/content"
    final = "https://cdn.example/final"
    transport = ScriptedTransport(
        {
            start: response(302, headers=(("Location", middle),)),
            middle: response(307, headers=(("Location", "/final"),)),
            final: response(body=b"public"),
        }
    )
    policy = DestinationPolicy(
        StaticResolver(
            {
                "public.example": ("8.8.8.8",),
                "cdn.example": ("2606:4700:4700::1111",),
            }
        )
    )

    result = await FetchService(transport, policy).fetch(start)

    assert result.content == "public"
    assert result.final_url == final
    assert transport.requests == [start, middle, final]


@pytest.mark.asyncio
async def test_bounds_redirect_chains() -> None:
    first = "https://public.example/one"
    second = "https://public.example/two"
    transport = ScriptedTransport(
        {
            first: response(302, headers=(("Location", second),)),
            second: response(302, headers=(("Location", first),)),
        }
    )
    service = FetchService(
        transport, DestinationPolicy(StaticResolver({"public.example": ("8.8.8.8",)}))
    )

    with pytest.raises(UpstreamError, match="redirect limit"):
        await service.fetch(first)

    assert len(transport.requests) == 6
