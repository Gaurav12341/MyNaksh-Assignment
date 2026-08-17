import asyncio
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

import httpx

from app.core.cache import cache
from app.core.logging import get_logger
from app.models.context import SourceResult


@dataclass(frozen=True)
class ServicePolicy:
    name: str
    path: str
    cache_key: str
    ttl_seconds: int
    timeout_seconds: float
    retries: int
    required: bool = False
    params: dict[str, str] = field(default_factory=dict)


class UpstreamClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.logger = get_logger(self.__class__.__name__)

    async def fetch(self, policy: ServicePolicy) -> SourceResult:
        cached = await cache.get(policy.cache_key)
        if cached is not None:
            return SourceResult(name=policy.name, data=cached, cache_hit=True, latency_ms=0.0)

        url = f"{self.base_url}{policy.path}"
        start = perf_counter()
        last_error = None

        for attempt in range(1, policy.retries + 2):
            try:
                async with httpx.AsyncClient(timeout=policy.timeout_seconds) as client:
                    response = await client.get(url, params=policy.params)
                    response.raise_for_status()
                    data: Any = response.json()
                    latency_ms = round((perf_counter() - start) * 1000, 2)
                    await cache.set(policy.cache_key, data, policy.ttl_seconds)
                    self.logger.info(
                        "upstream_fetch_success",
                        extra={
                            "request_id": "-",
                            "user_id": "-",
                            "intent": "-",
                            "source": policy.name,
                            "attempt": attempt,
                            "latency_ms": latency_ms,
                            "cache_hit": False,
                        },
                    )
                    return SourceResult(name=policy.name, data=data, latency_ms=latency_ms)
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                last_error = str(exc)
                if attempt <= policy.retries:
                    await asyncio.sleep(0.1 * attempt)

        latency_ms = round((perf_counter() - start) * 1000, 2)
        self.logger.warning(
            "upstream_fetch_failed",
            extra={
                "request_id": "-",
                "user_id": "-",
                "intent": "-",
                "source": policy.name,
                "latency_ms": latency_ms,
                "error": last_error,
            },
        )
        return SourceResult(name=policy.name, failed=True, error=last_error, latency_ms=latency_ms)
