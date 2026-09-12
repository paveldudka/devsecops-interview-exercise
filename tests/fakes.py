"""Deterministic test transport with no network access."""

from collections.abc import Iterable

from content_fetcher.destination_policy import DestinationPolicy, StaticResolver
from content_fetcher.transport import HttpResponse


class ScriptedTransport:
    """Return fixed responses and record requested URLs."""

    def __init__(self, responses: dict[str, HttpResponse]) -> None:
        self._responses = responses
        self.requests: list[str] = []

    async def get(self, url: str) -> HttpResponse:
        self.requests.append(url)
        try:
            return self._responses[url]
        except KeyError as exc:
            raise AssertionError(f"unexpected outbound request: {url}") from exc


def response(
    status_code: int = 200,
    *,
    headers: Iterable[tuple[str, str]] = (),
    body: bytes = b"",
) -> HttpResponse:
    return HttpResponse(status_code, dict(headers), body)


def public_destination_policy() -> DestinationPolicy:
    """Return deterministic globally routable answers for visible test hosts."""

    return DestinationPolicy(
        StaticResolver(
            {
                "public.example": ("8.8.8.8",),
                "cdn.example": ("2606:4700:4700::1111",),
            }
        )
    )
