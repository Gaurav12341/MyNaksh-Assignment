from datetime import date

from app.services.clients.base import ServicePolicy, UpstreamClient


class PanchangClient(UpstreamClient):
    async def get_panchang(self, data_source: str = "mock"):
        today = date.today().isoformat()
        return await self.fetch(
            ServicePolicy(
                name="Panchang",
                path="/mock/panchang",
                cache_key=f"{data_source}:panchang:{today}",
                ttl_seconds=86400,
                timeout_seconds=1.0,
                retries=2,
                params={"dataSource": data_source},
            )
        )
