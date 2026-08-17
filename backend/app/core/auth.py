from fastapi import Depends, Header

from app.core.errors import api_error
from app.core.security import verify_token
from app.db.repositories import UserRepository


async def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise api_error(401, "AUTH_REQUIRED", "Authentication is required.")
    token = authorization.split(" ", 1)[1].strip()
    claims = verify_token(token)
    if not claims:
        raise api_error(401, "INVALID_TOKEN", "Invalid or expired token.")

    user = UserRepository().find_by_guid(claims.get("sub", ""))
    if user is None:
        raise api_error(401, "USER_NOT_FOUND", "Authenticated user no longer exists.")
    return user


async def require_admin(current_user=Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise api_error(403, "ADMIN_REQUIRED", "Admin access is required.")
    return current_user


def ensure_can_access_user(current_user: dict, requested_user_id: str) -> None:
    if current_user.get("role") == "admin":
        return
    if current_user.get("id") != requested_user_id:
        raise api_error(403, "FORBIDDEN_USER_CONTEXT", "You can only request personalization for your own user profile.")
