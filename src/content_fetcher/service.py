"""Application behavior for retrieving URL content."""

from urllib.parse import urljoin, urlsplit

from content_fetcher.models import FetchResult
from content_fetcher.transport import HttpTransport


class FetchError(Exception):
    """A fetch request could not be completed."""


class FetchService:
    """Retrieve content while preserving normal HTTP redirect behavior."""

    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    async def fetch(self, requested_url: str) -> FetchResult:
        current_url = requested_url

        while True:
            self._validate_url(current_url)
            response = await self._transport.get(current_url)

            location = response.headers.get("location")
            if 300 <= response.status_code < 400 and location:
                current_url = urljoin(current_url, location)
                continue

            if response.status_code >= 400:
                raise FetchError(
                    f"upstream returned {response.status_code} for {current_url}"
                )

            content_type = response.headers.get("content-type")
            return FetchResult(
                requested_url=requested_url,
                final_url=current_url,
                content_type=content_type,
                content=response.body.decode("utf-8", errors="replace"),
                bytes_read=len(response.body),
            )

    @staticmethod
    def _validate_url(url: str) -> None:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise FetchError("URL must use HTTP or HTTPS and include a hostname")
        if parsed.username is not None or parsed.password is not None:
            raise FetchError("URLs containing user information are not supported")
