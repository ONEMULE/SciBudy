from __future__ import annotations

from research_mcp.cache import SQLiteStateStore


class RateLimiter:
    def __init__(self, state: SQLiteStateStore) -> None:
        self._state = state

    def wait(self, bucket: str, min_interval_sec: float) -> None:
        self._state.throttle(bucket=bucket, min_interval_sec=min_interval_sec)
