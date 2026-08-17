from uuid import uuid4

from fastapi import APIRouter, Depends
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.core.auth import get_current_user, require_admin
from app.core.errors import api_error
from app.core.logging import get_logger
from app.core.security import create_token, hash_password, verify_password
from app.db.repositories import UserRepository
from app.models.auth import AuthResponse, AuthUser, LoginRequest, RegisterRequest, UserOption

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    user = UserRepository().find_auth_user(payload.usernameOrEmail)
    if user is None or not verify_password(payload.password, user.get("passwordHash", ""), user.get("passwordSalt", "")):
        logger.warning("auth_login_failed username_or_email=%s", payload.usernameOrEmail)
        raise api_error(401, "INVALID_CREDENTIALS", "Invalid username/email or password.")
    logger.info(
        "auth_login_success user_id=%s user_guid=%s role=%s subscription=%s",
        user.get("id"),
        user.get("_id"),
        user.get("role"),
        user.get("subscription"),
    )
    return build_auth_response(user)


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest):
    password_hash, password_salt = hash_password(payload.password)
    subscription = payload.subscription
    billing_period = payload.billingPeriod if subscription == "premium" else None
    username = payload.username.strip().lower()
    email = str(payload.email).strip().lower()
    user_guid = str(uuid4())
    user_id = f"user_{user_guid[:8]}"
    document = {
        "_id": user_guid,
        "id": user_id,
        "name": payload.name.strip(),
        "username": username,
        "email": email,
        "passwordHash": password_hash,
        "passwordSalt": password_salt,
        "role": "user",
        "language": payload.language,
        "subscription": subscription,
        "billingPeriod": billing_period,
        "tonePreference": payload.tonePreference,
        "birthDetails": {"date": None, "time": None, "place": None},
    }
    try:
        user = UserRepository().create_user(document)
    except DuplicateKeyError as exc:
        raise api_error(409, "USER_EXISTS", "Username or email already exists.") from exc
    except PyMongoError as exc:
        raise api_error(503, "MONGODB_UNAVAILABLE", "MongoDB is unavailable.") from exc
    logger.info(
        "auth_register_success user_id=%s user_guid=%s role=%s subscription=%s",
        user.get("id"),
        user.get("_id"),
        user.get("role"),
        user.get("subscription"),
    )
    return build_auth_response(user)


@router.get("/me", response_model=AuthUser)
async def me(current_user=Depends(get_current_user)):
    return to_auth_user(current_user)


@router.get("/users", response_model=list[UserOption])
async def list_users(current_user=Depends(require_admin)):
    return [
        UserOption(
            guid=user["_id"],
            id=user["id"],
            name=user["name"],
            email=user["email"],
            subscription=user.get("subscription", "free"),
            role=user.get("role", "user"),
        )
        for user in UserRepository().list_users()
    ]


def build_auth_response(user: dict) -> AuthResponse:
    auth_user = to_auth_user(user)
    token = create_token({"sub": auth_user.guid, "role": auth_user.role, "userId": auth_user.id})
    return AuthResponse(token=token, user=auth_user)


def to_auth_user(user: dict) -> AuthUser:
    return AuthUser(
        guid=user["_id"],
        id=user["id"],
        name=user["name"],
        username=user["username"],
        email=user["email"],
        role=user.get("role", "user"),
        subscription=user.get("subscription", "free"),
        billingPeriod=user.get("billingPeriod"),
        language=user.get("language", "en"),
        tonePreference=user.get("tonePreference", "practical"),
    )
