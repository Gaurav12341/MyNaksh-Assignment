from app.services.clients.base import ServicePolicy, UpstreamClient


class HoroscopeClient(UpstreamClient):
    async def get_horoscope(self, user_id: str, data_source: str = "mock"):
        return await self.fetch(
            ServicePolicy(
                name="Horoscope",
                path=f"/mock/horoscope/{user_id}",
                cache_key=f"{data_source}:horoscope:{user_id}",
                ttl_seconds=600,
                timeout_seconds=1.5,
                retries=2,
                params={"dataSource": data_source},
            )
        )
