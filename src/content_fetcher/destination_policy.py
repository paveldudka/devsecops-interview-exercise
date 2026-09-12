"""Application-layer policy for outbound URL destinations."""

import asyncio
import ipaddress
import socket
from collections.abc import Mapping, Sequence
from typing import Protocol
from urllib.parse import urlsplit

IpAddress = ipaddress.IPv4Address | ipaddress.IPv6Address


class ResolutionError(Exception):
    """A hostname could not be resolved for policy evaluation."""


class DestinationDenied(Exception):
    """A destination is outside the service's allowed network boundary."""


class HostResolver(Protocol):
    """Resolve a hostname into all addresses used for policy evaluation."""

    async def resolve(self, hostname: str) -> Sequence[IpAddress]:
        """Return every address associated with the hostname."""
        ...


class SocketResolver:
    """Resolve hostnames with the runtime's configured resolver."""

    async def resolve(self, hostname: str) -> Sequence[IpAddress]:
        loop = asyncio.get_running_loop()
        try:
            records = await loop.getaddrinfo(
                hostname,
                None,
                family=socket.AF_UNSPEC,
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror as exc:
            raise ResolutionError("destination hostname could not be resolved") from exc

        addresses = {ipaddress.ip_address(record[4][0]) for record in records}
        if not addresses:
            raise ResolutionError("destination hostname returned no addresses")
        return tuple(sorted(addresses, key=str))


class StaticResolver:
    """Deterministic resolver for tests and the confidential evaluator."""

    def __init__(self, answers: Mapping[str, Sequence[str]]) -> None:
        self._answers = answers

    async def resolve(self, hostname: str) -> Sequence[IpAddress]:
        try:
            return tuple(
                ipaddress.ip_address(value) for value in self._answers[hostname]
            )
        except KeyError as exc:
            raise ResolutionError("destination hostname could not be resolved") from exc


class DestinationPolicy:
    """Allow only destinations whose evaluated addresses are globally routable."""

    def __init__(self, resolver: HostResolver) -> None:
        self._resolver = resolver

    async def validate(self, url: str) -> None:
        hostname = urlsplit(url).hostname
        if hostname is None:
            raise DestinationDenied("destination has no hostname")

        try:
            addresses: Sequence[IpAddress] = (ipaddress.ip_address(hostname),)
        except ValueError:
            addresses = await self._resolver.resolve(hostname)

        if not addresses or any(not address.is_global for address in addresses):
            raise DestinationDenied("destination is not permitted")
