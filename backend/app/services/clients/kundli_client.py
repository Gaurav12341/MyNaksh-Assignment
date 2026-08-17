from app.services.clients.base import ServicePolicy, UpstreamClient


class KundliClient(UpstreamClient):
    async def get_kundli(self, user_id: str, data_source: str = "mock"):
        return await self.fetch(
            ServicePolicy(
                name="Kundli",
                path=f"/mock/kundli/{user_id}",
                cache_key=f"{data_source}:kundli:{user_id}",
                ttl_seconds=3600,
                timeout_seconds=2.0,
                retries=2,
                params={"dataSource": data_source},
            )
        )
