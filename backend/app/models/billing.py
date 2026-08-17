from typing import Literal

from pydantic import BaseModel


BillingPeriod = Literal["weekly", "monthly", "yearly"]


class CheckoutRequest(BaseModel):
    billingPeriod: BillingPeriod


class CheckoutResponse(BaseModel):
    provider: Literal["stripe", "mock"]
    checkoutUrl: str
    sessionId: str
