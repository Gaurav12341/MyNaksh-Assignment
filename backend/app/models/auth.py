from typing import Literal

from pydantic import BaseModel, EmailStr, Field


Role = Literal["user", "admin"]
Subscription = Literal["free", "premium"]
BillingPeriod = Literal["weekly", "monthly", "yearly"]


class LoginRequest(BaseModel):
    usernameOrEmail: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1)
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)
    subscription: Subscription = "free"
    billingPeriod: BillingPeriod | None = None
    language: str = "en"
    tonePreference: str = "practical"


class AuthUser(BaseModel):
    guid: str
    id: str
    name: str
    username: str
    email: str
    role: Role
    subscription: Subscription
    billingPeriod: BillingPeriod | None = None
    language: str = "en"
    tonePreference: str = "practical"


class AuthResponse(BaseModel):
    token: str
    user: AuthUser


class UserOption(BaseModel):
    guid: str
    id: str
    name: str
    email: str
    subscription: str
    role: str
