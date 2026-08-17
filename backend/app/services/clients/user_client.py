from app.services.clients.base import ServicePolicy, UpstreamClient


class UserClient(UpstreamClient):
    async def get_user(self, user_id: str, data_source: str = "mock"):
        return await self.fetch(
            ServicePolicy(
                name="User Profile",
                path=f"/mock/users/{user_id}",
                cache_key=f"{data_source}:user:{user_id}",
                ttl_seconds=300,
                timeout_seconds=1.5,
                retries=2,
                required=True,
                params={"dataSource": data_source},
            )
        )
