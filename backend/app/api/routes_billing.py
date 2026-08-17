from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.repositories import UserRepository
from app.models.billing import CheckoutRequest, CheckoutResponse

router = APIRouter(prefix="/billing", tags=["billing"])
logger = get_logger(__name__)


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(payload: CheckoutRequest, current_user=Depends(get_current_user)):
    settings = get_settings()
    price_id = {
        "weekly": settings.stripe_weekly_price_id,
        "monthly": settings.stripe_monthly_price_id,
        "yearly": settings.stripe_yearly_price_id,
    }[payload.billingPeriod]

    if not settings.stripe_secret_key or not price_id:
        UserRepository().update_subscription(current_user["_id"], "premium", payload.billingPeriod)
        logger.info(
            "billing_mock_checkout user_id=%s user_guid=%s billing_period=%s",
            current_user.get("id"),
            current_user.get("_id"),
            payload.billingPeriod,
        )
        return CheckoutResponse(
            provider="mock",
            checkoutUrl=f"{settings.frontend_base_url}?payment=mock-success&period={payload.billingPeriod}",
            sessionId=f"mock_checkout_{current_user['_id']}_{payload.billingPeriod}",
        )

    import stripe

    stripe.api_key = settings.stripe_secret_key
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        customer_email=current_user["email"],
        success_url=f"{settings.frontend_base_url}?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.frontend_base_url}?payment=cancelled",
        metadata={"userGuid": current_user["_id"], "billingPeriod": payload.billingPeriod},
    )
    logger.info(
        "billing_stripe_checkout_created user_id=%s user_guid=%s billing_period=%s session_id=%s",
        current_user.get("id"),
        current_user.get("_id"),
        payload.billingPeriod,
        session.id,
    )
    return CheckoutResponse(provider="stripe", checkoutUrl=session.url, sessionId=session.id)
