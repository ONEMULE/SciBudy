from __future__ import annotations

from abc import ABC, abstractmethod

from research_mcp.client import ResearchHttpClient
from research_mcp.models import LiteratureResult
from research_mcp.settings import Settings


class BaseProvider(ABC):
    name = "base"
    cache_ttl_sec = 6 * 60 * 60
    min_interval_sec = 0.5
    enabled_flag = ""
    required_settings: tuple[tuple[str, str], ...] = ()

    def __init__(self, settings: Settings, client: ResearchHttpClient) -> None:
        self.settings = settings
        self.client = client

    def ready(self) -> tuple[bool, str | None]:
        if self.enabled_flag and not getattr(self.settings, self.enabled_flag):
            return False, "disabled by configuration"
        for env_name, attr_name in self.required_settings:
            value = getattr(self.settings, attr_name)
            if not value:
                return False, f"missing {env_name}"
        return True, None

    @abstractmethod
    def search(self, query: str, limit: int, sort: str) -> list[LiteratureResult]:
        raise NotImplementedError
