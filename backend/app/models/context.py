from typing import Any

from pydantic import BaseModel


class SourceResult(BaseModel):
    name: str
    data: Any | None = None
    failed: bool = False
    error: str | None = None
    latency_ms: float | None = None
    cache_hit: bool = False


class UserContextBundle(BaseModel):
    user: SourceResult
    kundli: SourceResult
    horoscope: SourceResult
    panchang: SourceResult

    @property
    def failed_sources(self) -> list[str]:
        return [result.name for result in [self.user, self.kundli, self.horoscope, self.panchang] if result.failed]

    @property
    def available_sources(self) -> list[str]:
        return [result.name for result in [self.user, self.kundli, self.horoscope, self.panchang] if not result.failed]

    def as_resolver_data(self) -> dict[str, Any]:
        return {
            "user": self.user.data or {},
            "kundli": self.kundli.data or {},
            "horoscope": self.horoscope.data or {},
            "panchang": self.panchang.data or {},
        }
