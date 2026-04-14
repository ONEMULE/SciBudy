from __future__ import annotations

import hashlib
import json
import time
from typing import Any

import httpx

from research_mcp.cache import SQLiteStateStore
from research_mcp.errors import ProviderRequestError
from research_mcp.rate_limit import RateLimiter
from research_mcp.settings import Settings


class ResearchHttpClient:
    RETRIABLE_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        settings: Settings,
        state: SQLiteStateStore,
        rate_limiter: RateLimiter,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._settings = settings
        self._state = state
        self._rate_limiter = rate_limiter
        self._client = httpx.Client(
            timeout=settings.request_timeout_sec,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def get_text(
        self,
        provider_name: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        ttl_sec: float,
        min_interval_sec: float,
    ) -> tuple[str, bool]:
        cache_key = self._cache_key(provider_name, url, params)
        cached = self._state.get_cache(cache_key)
        if cached is not None:
            return cached, True

        last_exception: Exception | None = None
        for attempt in range(self._settings.max_retries + 1):
            self._rate_limiter.wait(provider_name, min_interval_sec)
            try:
                response = self._client.get(url, params=params, headers=headers)
                if response.status_code in self.RETRIABLE_STATUS_CODES and attempt < self._settings.max_retries:
                    time.sleep(self._backoff(attempt))
                    continue
                response.raise_for_status()
                body = response.text
                self._state.set_cache(cache_key, body, ttl_sec=ttl_sec)
                return body, False
            except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
                last_exception = exc
                if attempt < self._settings.max_retries:
                    time.sleep(self._backoff(attempt))
                    continue
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                snippet = exc.response.text[:300].replace("\n", " ")
                if status_code in self.RETRIABLE_STATUS_CODES and attempt < self._settings.max_retries:
                    time.sleep(self._backoff(attempt))
                    continue
                raise ProviderRequestError(
                    f"{provider_name} returned HTTP {status_code}: {snippet}"
                ) from exc
        raise ProviderRequestError(f"{provider_name} request failed: {last_exception}") from last_exception

    def get_json(
        self,
        provider_name: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        ttl_sec: float,
        min_interval_sec: float,
    ) -> tuple[Any, bool]:
        body, cached = self.get_text(
            provider_name=provider_name,
            url=url,
            params=params,
            headers=headers,
            ttl_sec=ttl_sec,
            min_interval_sec=min_interval_sec,
        )
        try:
            return json.loads(body), cached
        except json.JSONDecodeError as exc:
            raise ProviderRequestError(f"{provider_name} returned invalid JSON") from exc

    def _cache_key(self, provider_name: str, url: str, params: dict[str, Any] | None) -> str:
        payload = json.dumps(
            {"provider": provider_name, "url": url, "params": params or {}},
            sort_keys=True,
            default=str,
        )
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return f"{provider_name}:{digest}"

    def _backoff(self, attempt: int) -> float:
        return self._settings.backoff_base_sec * (2**attempt)
