"""Public request and response models."""

from pydantic import BaseModel, Field


class FetchRequest(BaseModel):
    """A request to retrieve content from a URL."""

    url: str = Field(min_length=1, max_length=4096)


class FetchResult(BaseModel):
    """Content returned by the fetch service."""

    requested_url: str
    final_url: str
    content_type: str | None
    content: str
    bytes_read: int
