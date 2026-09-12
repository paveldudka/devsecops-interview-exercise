#!/usr/bin/env python3
"""Confidential behavioral checks for the starter and reference solution."""

import argparse
import asyncio
from dataclasses import dataclass

from content_fetcher.service import FetchError, FetchService
from content_fetcher.transport import HttpResponse


@dataclass
class TrackingTransport:
    responses: dict[str, HttpResponse]

    def __post_init__(self) -> None:
        self.requests: list[str] = []

    async def get(self, url: str) -> HttpResponse:
        self.requests.append(url)
        return self.responses[url]


def build_service(transport: TrackingTransport) -> FetchService:
    """Construct either starter or reference service without static assumptions."""

    try:
        from content_fetcher.destination_policy import (
            DestinationPolicy,
            StaticResolver,
        )
    except ImportError:
        return FetchService(transport)  # type: ignore[call-arg]

    resolver = StaticResolver(
        {
            "public.example": ("8.8.8.8",),
            "internal.example": ("10.0.0.8",),
        }
    )
    return FetchService(transport, DestinationPolicy(resolver))


async def request_is_blocked(url: str) -> tuple[bool, list[str]]:
    transport = TrackingTransport({url: HttpResponse(200, {}, b"sensitive")})
    try:
        await build_service(transport).fetch(url)
    except FetchError:
        return True, transport.requests
    return False, transport.requests


async def redirect_is_blocked() -> tuple[bool, list[str]]:
    start = "https://public.example/start"
    protected = "http://internal.example/data"
    transport = TrackingTransport(
        {
            start: HttpResponse(302, {"Location": protected}, b""),
            protected: HttpResponse(200, {}, b"sensitive"),
        }
    )
    try:
        await build_service(transport).fetch(start)
    except FetchError:
        return True, transport.requests
    return False, transport.requests


async def public_chain_works() -> bool:
    start = "https://public.example/start"
    final = "https://public.example/final"
    transport = TrackingTransport(
        {
            start: HttpResponse(302, {"Location": "/final"}, b""),
            final: HttpResponse(200, {}, b"public"),
        }
    )
    result = await build_service(transport).fetch(start)
    return result.content == "public" and transport.requests == [start, final]


async def evaluate(expectation: str) -> int:
    scenarios = {
        "IPv4 literal": await request_is_blocked("http://127.0.0.1/data"),
        "IPv6 literal": await request_is_blocked("http://[::1]/data"),
        "link-local literal": await request_is_blocked(
            "http://169.254.169.254/latest/data"
        ),
        "redirect target": await redirect_is_blocked(),
    }
    public_ok = await public_chain_works()

    for name, (blocked, requests) in scenarios.items():
        print(f"{name}: blocked={blocked}, outbound_requests={requests}")
    print(f"public redirect chain preserved: {public_ok}")

    blocked_values = [blocked for blocked, _ in scenarios.values()]
    if expectation == "unsafe":
        passed = not any(blocked_values) and public_ok
        summary = "starter exposes all modeled unsafe states"
    else:
        passed = all(blocked_values) and public_ok
        summary = "reference blocks modeled unsafe states and preserves behavior"

    print(f"RESULT: {'PASS' if passed else 'FAIL'} — {summary}")
    return 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect", choices=("unsafe", "safe"), required=True)
    args = parser.parse_args()
    return asyncio.run(evaluate(args.expect))


if __name__ == "__main__":
    raise SystemExit(main())
