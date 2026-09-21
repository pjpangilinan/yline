"""Async rate limiter for Groq API calls in the yline pipeline.

Maintains sliding-window rate limits across four standard Groq limits:
- Requests Per Minute (RPM): max 30
- Requests Per Day (RPD): max 14,400
- Tokens Per Minute (TPM): max 15,000
- Tokens Per Day (TPD): max 500,000

Uses asyncio.Lock for non-blocking asynchronous coordination within event loops,
threading.Lock for multi-threaded safety, and exact time-based sliding windows.
"""
from __future__ import annotations

import asyncio
import collections
import logging
import threading
import time
import weakref
from typing import Any

logger = logging.getLogger(__name__)

# Default Groq API limits (tier 1 / free defaults)
DEFAULT_MAX_REQUESTS_PER_MINUTE: int = 30
DEFAULT_MAX_REQUESTS_PER_DAY: int = 14_400
DEFAULT_MAX_TOKENS_PER_MINUTE: int = 15_000
DEFAULT_MAX_TOKENS_PER_DAY: int = 500_000

WINDOW_MINUTE_SECONDS: float = 60.0
WINDOW_DAY_SECONDS: float = 86_400.0


class _RequestRecord:
    """Internal record tracking an acquired API request and its token count.

    Attributes:
        timestamp: Monotonic clock timestamp when request was acquired.
        tokens: Estimated or reconciled actual token count.
        is_pending: True if waiting for actual token usage via record_usage().
    """

    __slots__ = ("timestamp", "tokens", "is_pending")

    def __init__(self, timestamp: float, tokens: int, is_pending: bool = True) -> None:
        self.timestamp: float = timestamp
        self.tokens: int = tokens
        self.is_pending: bool = is_pending


class RateLimiter:
    """Thread-safe, singleton async rate limiter for LLM API calls.

    Enforces sliding-window rate limits for requests and tokens over 1-minute
    and 1-day windows.

    Typical usage:
        from yline.rate_limiter import rate_limiter

        # Before making an API call:
        await rate_limiter.acquire(estimated_tokens=300)

        # After the API response returns:
        rate_limiter.record_usage(prompt_tokens=180, completion_tokens=45)
    """

    _instance: RateLimiter | None = None
    _singleton_lock: threading.Lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> RateLimiter:
        """Ensure a single shared instance across threads and imports."""
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        max_requests_per_minute: int = DEFAULT_MAX_REQUESTS_PER_MINUTE,
        max_requests_per_day: int = DEFAULT_MAX_REQUESTS_PER_DAY,
        max_tokens_per_minute: int = DEFAULT_MAX_TOKENS_PER_MINUTE,
        max_tokens_per_day: int = DEFAULT_MAX_TOKENS_PER_DAY,
    ) -> None:
        """Initialize the rate limiter. Guarded against multiple executions."""
        if getattr(self, "_initialized", False):
            return

        with self._singleton_lock:
            if getattr(self, "_initialized", False):
                return

            self.max_requests_per_minute: int = max_requests_per_minute
            self.max_requests_per_day: int = max_requests_per_day
            self.max_tokens_per_minute: int = max_tokens_per_minute
            self.max_tokens_per_day: int = max_tokens_per_day

            self._thread_lock: threading.Lock = threading.Lock()
            # Weak key dictionary mapping event loops to loop-specific asyncio.Locks
            # to guarantee thread-safe asyncio concurrency across separate event loops.
            self._async_locks: weakref.WeakKeyDictionary[
                asyncio.AbstractEventLoop, asyncio.Lock
            ] = weakref.WeakKeyDictionary()

            # Sliding window storage
            self._history: collections.deque[_RequestRecord] = collections.deque()
            self._pending: collections.deque[_RequestRecord] = collections.deque()
            self._day_token_sum: int = 0

            self._initialized: bool = True

    def _get_async_lock(self) -> asyncio.Lock:
        """Retrieve or create an asyncio.Lock bound to the current running event loop."""
        loop = asyncio.get_running_loop()
        with self._thread_lock:
            lock = self._async_locks.get(loop)
            if lock is None:
                lock = asyncio.Lock()
                self._async_locks[loop] = lock
            return lock

    @property
    def _async_lock(self) -> asyncio.Lock:
        """Access the asyncio.Lock for the current running event loop."""
        return self._get_async_lock()

    def _prune_history(self, now: float) -> None:
        """Evict records older than 24 hours and discard stale pending reservations.

        Must be called while holding self._thread_lock.
        """
        day_cutoff = now - WINDOW_DAY_SECONDS
        while self._history and self._history[0].timestamp < day_cutoff:
            popped = self._history.popleft()
            self._day_token_sum -= popped.tokens

        # Discard unfulfilled pending records older than 10 minutes to prevent memory leak
        # if an external request crashed and never called record_usage().
        stale_pending_cutoff = now - 600.0
        while self._pending and self._pending[0].timestamp < stale_pending_cutoff:
            self._pending.popleft()

    def _calculate_wait_time(self, now: float, estimated_tokens: int) -> float:
        """Compute minimum seconds to wait before limits permit a new request.

        Must be called while holding self._thread_lock.

        Args:
            now: Current monotonic timestamp.
            estimated_tokens: Token count estimated for the incoming request.

        Returns:
            Wait duration in seconds (0.0 if request can proceed immediately).
        """
        minute_cutoff = now - WINDOW_MINUTE_SECONDS

        # Collect records within the 1-minute sliding window (chronological order)
        minute_records: list[_RequestRecord] = []
        minute_tokens: int = 0
        for record in reversed(self._history):
            if record.timestamp < minute_cutoff:
                break
            minute_records.append(record)
            minute_tokens += record.tokens
        minute_records.reverse()
        minute_count = len(minute_records)

        wait_rpm = 0.0
        if minute_count + 1 > self.max_requests_per_minute:
            excess = (minute_count + 1) - self.max_requests_per_minute
            wait_rpm = max(
                0.0, (minute_records[excess - 1].timestamp + WINDOW_MINUTE_SECONDS) - now
            )

        wait_rpd = 0.0
        day_count = len(self._history)
        if day_count + 1 > self.max_requests_per_day:
            excess = (day_count + 1) - self.max_requests_per_day
            wait_rpd = max(
                0.0, (self._history[excess - 1].timestamp + WINDOW_DAY_SECONDS) - now
            )

        wait_tpm = 0.0
        if minute_tokens + estimated_tokens > self.max_tokens_per_minute:
            needed_tpm = (minute_tokens + estimated_tokens) - self.max_tokens_per_minute
            accum = 0
            for record in minute_records:
                accum += record.tokens
                if accum >= needed_tpm:
                    wait_tpm = max(
                        0.0, (record.timestamp + WINDOW_MINUTE_SECONDS) - now
                    )
                    break

        wait_tpd = 0.0
        if self._day_token_sum + estimated_tokens > self.max_tokens_per_day:
            needed_tpd = (self._day_token_sum + estimated_tokens) - self.max_tokens_per_day
            accum = 0
            for record in self._history:
                accum += record.tokens
                if accum >= needed_tpd:
                    wait_tpd = max(0.0, (record.timestamp + WINDOW_DAY_SECONDS) - now)
                    break

        wait_time = max(wait_rpm, wait_rpd, wait_tpm, wait_tpd, 0.0)
        if wait_time > 0:
            # Small safety buffer to ensure window threshold has completely elapsed
            wait_time += 0.02
        return wait_time

    def _record_acquisition(self, now: float, estimated_tokens: int) -> None:
        """Register an acquired request slot with its estimated tokens.

        Must be called while holding self._thread_lock.
        """
        record = _RequestRecord(timestamp=now, tokens=estimated_tokens, is_pending=True)
        self._history.append(record)
        self._pending.append(record)
        self._day_token_sum += estimated_tokens

    async def acquire(self, estimated_tokens: int = 100) -> None:
        """Block asynchronously until rate limits allow proceeding.

        Checks sliding windows for RPM, RPD, TPM, and TPD. If any limit is
        reached, sleeps until sufficient capacity becomes available, then
        records the request and token reservation.

        Args:
            estimated_tokens: Estimated prompt + completion tokens for the upcoming
                call (default: 100).

        Raises:
            ValueError: If estimated_tokens is negative or exceeds the maximum
                per-minute or per-day token limit.
        """
        if estimated_tokens < 0:
            raise ValueError(f"estimated_tokens must be non-negative, got {estimated_tokens}")
        if estimated_tokens > self.max_tokens_per_minute:
            raise ValueError(
                f"estimated_tokens ({estimated_tokens}) exceeds maximum tokens per minute "
                f"({self.max_tokens_per_minute})"
            )
        if estimated_tokens > self.max_tokens_per_day:
            raise ValueError(
                f"estimated_tokens ({estimated_tokens}) exceeds maximum tokens per day "
                f"({self.max_tokens_per_day})"
            )

        async_lock = self._get_async_lock()
        async with async_lock:
            while True:
                with self._thread_lock:
                    now = time.monotonic()
                    self._prune_history(now)
                    wait_time = self._calculate_wait_time(now, estimated_tokens)
                    if wait_time <= 0:
                        self._record_acquisition(now, estimated_tokens)
                        return

                logger.info(
                    f"Rate limit reached. Sleeping {wait_time:.2f}s before retrying acquire..."
                )
                await asyncio.sleep(wait_time)

    def record_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Update token counters with actual usage after an API call completes.

        Reconciles the oldest pending estimated token reservation with the actual
        tokens reported in the API response metadata. If no pending reservation
        is found, records actual usage directly.

        Args:
            prompt_tokens: Input tokens used in prompt.
            completion_tokens: Output tokens generated by the model.
        """
        actual_tokens = max(0, prompt_tokens + completion_tokens)

        with self._thread_lock:
            now = time.monotonic()
            self._prune_history(now)

            if self._pending:
                record = self._pending.popleft()
                token_diff = actual_tokens - record.tokens
                record.tokens = actual_tokens
                record.is_pending = False
                self._day_token_sum += token_diff
            else:
                record = _RequestRecord(timestamp=now, tokens=actual_tokens, is_pending=False)
                self._history.append(record)
                self._day_token_sum += actual_tokens

    def get_status(self) -> dict[str, Any]:
        """Return current rate limiter metrics and remaining capacities.

        Returns:
            Dictionary containing current requests and tokens consumed vs limits.
        """
        with self._thread_lock:
            now = time.monotonic()
            self._prune_history(now)

            minute_cutoff = now - WINDOW_MINUTE_SECONDS
            minute_records = [r for r in self._history if r.timestamp >= minute_cutoff]
            minute_tokens = sum(r.tokens for r in minute_records)

            return {
                "requests_last_minute": len(minute_records),
                "max_requests_per_minute": self.max_requests_per_minute,
                "requests_last_day": len(self._history),
                "max_requests_per_day": self.max_requests_per_day,
                "tokens_last_minute": minute_tokens,
                "max_tokens_per_minute": self.max_tokens_per_minute,
                "tokens_last_day": self._day_token_sum,
                "max_tokens_per_day": self.max_tokens_per_day,
                "pending_reservations": len(self._pending),
            }

    def reset(self) -> None:
        """Reset all rate limiter counters and history (primarily for tests)."""
        with self._thread_lock:
            self._history.clear()
            self._pending.clear()
            self._day_token_sum = 0


# Shared singleton instance and alias
GroqRateLimiter = RateLimiter
rate_limiter = RateLimiter()

__all__ = [
    "RateLimiter",
    "GroqRateLimiter",
    "rate_limiter",
]
