"""Custom exceptions and retry utilities for the yline lyric video pipeline.

Provides structured domain exceptions for each stage of the pipeline (metadata resolution,
lyrics retrieval, media downloads, video rendering) and a configured Tenacity retry decorator
with exponential backoff.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, TypeVar, overload

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class YLineError(Exception):
    """Base exception class for all yline pipeline errors.

    Attributes:
        message: Human-readable description of the error.
        details: Optional supplementary metadata or diagnostic context.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (details: {self.details})"
        return self.message


class MetadataNotFound(YLineError):
    """Raised when song metadata cannot be resolved from queries or external databases."""

    def __init__(
        self,
        query: str,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        msg = message or f"No metadata found for query: '{query}'"
        super().__init__(msg, details=details or {"query": query})


class LyricsNotFound(YLineError):
    """Raised when synced or plain text lyrics cannot be found for a resolved song."""

    def __init__(
        self,
        song_title: str,
        artist: str | None = None,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        target = f"'{song_title}'" if not artist else f"'{song_title}' by {artist}"
        msg = message or f"Lyrics could not be found for {target}"
        merged_details = {"song_title": song_title, "artist": artist}
        if details:
            merged_details.update(details)
        super().__init__(msg, details=merged_details)


class ImageDownloadFailed(YLineError):
    """Raised when an image search or image download fails for a lyric line."""

    def __init__(
        self,
        url_or_query: str,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        msg = message or f"Failed to download image for: '{url_or_query}'"
        merged_details = {"url_or_query": url_or_query}
        if details:
            merged_details.update(details)
        super().__init__(msg, details=merged_details)


class AudioDownloadFailed(YLineError):
    """Raised when downloading or extracting audio stream/file fails."""

    def __init__(
        self,
        source: str,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        msg = message or f"Failed to download audio from source: '{source}'"
        merged_details = {"source": source}
        if details:
            merged_details.update(details)
        super().__init__(msg, details=merged_details)


class VideoAssemblyFailed(YLineError):
    """Raised when assembling audio, images, and lyric overlays into a video fails."""

    def __init__(
        self,
        message: str = "Failed to assemble video from pipeline assets",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details=details)


@overload
def retry_with_backoff(fn: F) -> F:
    ...


@overload
def retry_with_backoff(
    fn: None = None,
    *,
    max_retries: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    retry_exceptions: tuple[type[Exception], ...] = (Exception,),
    log_level: int = logging.WARNING,
) -> Callable[[F], F]:
    ...


def retry_with_backoff(
    fn: F | None = None,
    *,
    max_retries: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    retry_exceptions: tuple[type[Exception], ...] = (Exception,),
    log_level: int = logging.WARNING,
) -> F | Callable[[F], F]:
    """Retry decorator using Tenacity with exponential backoff.

    Applies exponential backoff with up to `max_retries` attempts (default 3),
    waiting between `min_wait` (1.0s) and `max_wait` (10.0s) before retrying.
    Works transparently on both synchronous and asynchronous (async def) callables.

    Can be used with or without decorator arguments:
        @retry_with_backoff
        def fetch_data(): ...

        @retry_with_backoff(max_retries=3, min_wait=2.0)
        async def fetch_async(): ...

    Args:
        fn: The function or coroutine function to wrap when called without parentheses.
        max_retries: Maximum number of execution attempts before reraising (default 3).
        min_wait: Minimum wait duration in seconds (default 1.0).
        max_wait: Maximum wait duration in seconds (default 10.0).
        retry_exceptions: Tuple of exception types that trigger a retry (default: Exception).
        log_level: Logging severity level for retry attempts (default: logging.WARNING).

    Returns:
        Decorated function or decorator callable.
    """
    decorator = retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=1.0, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(retry_exceptions),
        before_sleep=before_sleep_log(logger, log_level),
        reraise=True,
    )

    if fn is not None:
        return decorator(fn)
    return decorator


# Convenience alias for users expecting retry_decorator
retry_decorator = retry_with_backoff

__all__ = [
    "YLineError",
    "MetadataNotFound",
    "LyricsNotFound",
    "ImageDownloadFailed",
    "AudioDownloadFailed",
    "VideoAssemblyFailed",
    "retry_with_backoff",
    "retry_decorator",
]
