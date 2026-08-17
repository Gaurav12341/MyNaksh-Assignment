import asyncio
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import PyMongoError

from app.db.repositories import HoroscopeRepository, KundliRepository, PanchangRepository, UserRepository
from app.services.mocks.mock_data import HOROSCOPE, KUNDLI, PANCHANG, USER_PROFILES

router = APIRouter(tags=["mock-services"])


async def maybe_delay_or_fail(delay_ms: int, fail: bool) -> None:
    if delay_ms > 0:
        await asyncio.sleep(delay_ms / 1000)
    if fail:
        raise HTTPException(status_code=503, detail="Simulated upstream failure")


@router.get("/mock/users/{user_id}")
async def get_user(
    user_id: str,
    delayMs: int = Query(0, ge=0, le=5000),
    fail: bool = False,
    dataSource: Literal["mock", "mongodb"] = "mock",
):
    await maybe_delay_or_fail(delayMs, fail)
    if dataSource == "mongodb":
        try:
            user = UserRepository().find_user(user_id)
        except PyMongoError as exc:
            raise HTTPException(status_code=503, detail=f"MongoDB unavailable: {exc}") from exc
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    if user_id not in USER_PROFILES:
        raise HTTPException(status_code=404, detail="User not found")
    return USER_PROFILES[user_id]


@router.get("/mock/kundli/{user_id}")
async def get_kundli(
    user_id: str,
    delayMs: int = Query(0, ge=0, le=5000),
    fail: bool = False,
    dataSource: Literal["mock", "mongodb"] = "mock",
):
    await maybe_delay_or_fail(delayMs, fail)
    if dataSource == "mongodb":
        try:
            kundli = KundliRepository().find_kundli(user_id)
        except PyMongoError as exc:
            raise HTTPException(status_code=503, detail=f"MongoDB unavailable: {exc}") from exc
        if kundli is None:
            raise HTTPException(status_code=404, detail="Kundli not found")
        return kundli
    if user_id not in KUNDLI:
        raise HTTPException(status_code=404, detail="Kundli not found")
    return KUNDLI[user_id]


@router.get("/mock/horoscope/{user_id}")
async def get_horoscope(
    user_id: str,
    delayMs: int = Query(0, ge=0, le=5000),
    fail: bool = False,
    dataSource: Literal["mock", "mongodb"] = "mock",
):
    await maybe_delay_or_fail(delayMs, fail)
    if dataSource == "mongodb":
        try:
            horoscope = HoroscopeRepository().find_horoscope(user_id)
        except PyMongoError as exc:
            raise HTTPException(status_code=503, detail=f"MongoDB unavailable: {exc}") from exc
        if horoscope is None:
            raise HTTPException(status_code=404, detail="Horoscope not found")
        return horoscope
    if user_id not in HOROSCOPE:
        raise HTTPException(status_code=404, detail="Horoscope not found")
    return HOROSCOPE[user_id]


@router.get("/mock/panchang")
async def get_panchang(
    delayMs: int = Query(0, ge=0, le=5000),
    fail: bool = False,
    dataSource: Literal["mock", "mongodb"] = "mock",
):
    await maybe_delay_or_fail(delayMs, fail)
    if dataSource == "mongodb":
        try:
            panchang = PanchangRepository().find_panchang()
        except PyMongoError as exc:
            raise HTTPException(status_code=503, detail=f"MongoDB unavailable: {exc}") from exc
        if panchang is None:
            raise HTTPException(status_code=404, detail="Panchang not found")
        return panchang
    return PANCHANG
