from typing import Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MongoClientProvider:
    """Optional MongoDB hook for later POC expansion.

    The app intentionally runs without MongoDB. Keeping this boundary explicit
    makes it straightforward to add persistence without coupling it to mocks.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Any | None = None

    def get_client(self) -> Any | None:
        if not self.settings.mongo_uri:
            return None
        try:
            from pymongo import MongoClient
        except ImportError:
            logger.warning("mongo_driver_missing")
            return None

        if self._client is None:
            self._client = MongoClient(self.settings.mongo_uri, serverSelectionTimeoutMS=1500)
        return self._client

    def get_database(self) -> Any | None:
        client = self.get_client()
        if client is None:
            return None
        return client[self.settings.mongo_database]


mongo_provider = MongoClientProvider()
