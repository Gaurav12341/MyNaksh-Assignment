import asyncio

from app.core.config import Settings, get_settings
from app.core.errors import api_error
from app.models.context import UserContextBundle
from app.services.clients.horoscope_client import HoroscopeClient
from app.services.clients.kundli_client import KundliClient
from app.services.clients.panchang_client import PanchangClient
from app.services.clients.user_client import UserClient


class ContextFetcher:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        base_url = self.settings.mock_service_base_url
        self.user_client = UserClient(base_url)
        self.kundli_client = KundliClient(base_url)
        self.horoscope_client = HoroscopeClient(base_url)
        self.panchang_client = PanchangClient(base_url)

    async def fetch_all(self, user_id: str, request_id: str | None = None, data_source: str = "mock") -> UserContextBundle:
        user, kundli, horoscope, panchang = await asyncio.gather(
            self.user_client.get_user(user_id, data_source),
            self.kundli_client.get_kundli(user_id, data_source),
            self.horoscope_client.get_horoscope(user_id, data_source),
            self.panchang_client.get_panchang(data_source),
        )

        if user.failed:
            raise api_error(
                status_code=502,
                code="UPSTREAM_USER_UNAVAILABLE",
                message="Unable to fetch required user profile.",
                request_id=request_id,
            )

        return UserContextBundle(user=user, kundli=kundli, horoscope=horoscope, panchang=panchang)
