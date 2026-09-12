"""Application behavior for retrieving URL content."""

from urllib.parse import urljoin, urlsplit

from content_fetcher.destination_policy import (
    DestinationDenied,
    DestinationPolicy,
    ResolutionError,
)
from content_fetcher.models import FetchResult
from content_fetcher.transport import HttpTransport, TransportError


class FetchError(Exception):
    """A fetch request could not be completed."""


class InvalidUrlError(FetchError):
    """The supplied URL is not supported by the service."""


class UpstreamError(FetchError):
    """An upstream response could not satisfy the fetch request."""


class FetchService:
    """Retrieve content and follow HTTP redirect chains."""

    def __init__(
        self,
        transport: HttpTransport,
        destination_policy: DestinationPolicy,
        *,
        max_redirects: int = 5,
    ) -> None:
        self._transport = transport
        self._destination_policy = destination_policy
        self._max_redirects = max_redirects

    async def fetch(self, requested_url: str) -> FetchResult:
        self._validate_url(requested_url)
        current_url = requested_url
        redirects_followed = 0

        while True:
            if current_url != requested_url:
                try:
                    self._validate_url(current_url)
                except InvalidUrlError as exc:
                    raise UpstreamError("upstream returned invalid redirect") from exc
            try:
                await self._destination_policy.validate(current_url)
            except DestinationDenied as exc:
                if current_url == requested_url:
                    raise InvalidUrlError("destination is not permitted") from exc
                raise UpstreamError(
                    "upstream redirected to denied destination"
                ) from exc
            except ResolutionError as exc:
                raise UpstreamError("destination could not be resolved") from exc
            try:
                response = await self._transport.get(current_url)
            except TransportError as exc:
                raise UpstreamError("upstream request failed") from exc

            location = response.headers.get("location")
            if response.status_code in {301, 302, 303, 307, 308} and location:
                if redirects_followed >= self._max_redirects:
                    raise UpstreamError("upstream redirect limit exceeded")
                redirects_followed += 1
                try:
                    current_url = urljoin(current_url, location)
                except ValueError as exc:
                    raise UpstreamError("upstream returned invalid redirect") from exc
                continue

            if response.status_code in {301, 302, 303, 307, 308}:
                raise UpstreamError(
                    "upstream returned redirect "
                    f"{response.status_code} without location"
                )

            if 300 <= response.status_code < 400:
                raise UpstreamError(
                    f"upstream returned unexpected status {response.status_code}"
                )

            if response.status_code >= 400:
                raise UpstreamError(
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
        try:
            parsed = urlsplit(url)
        except ValueError as exc:
            raise InvalidUrlError("URL is malformed") from exc
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise InvalidUrlError("URL must use HTTP or HTTPS and include a hostname")
        if parsed.username is not None or parsed.password is not None:
            raise InvalidUrlError("URLs containing user information are not supported")
