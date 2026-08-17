from typing import Any

from app.db.mongo import mongo_provider


class UserRepository:
    def find_user(self, user_id: str) -> dict[str, Any] | None:
        db = mongo_provider.get_database()
        if db is None:
            return None
        return db.users.find_one({"id": user_id}, {"passwordHash": 0, "passwordSalt": 0})

    def find_by_guid(self, user_guid: str) -> dict[str, Any] | None:
        db = mongo_provider.get_database()
        if db is None:
            return None
        return db.users.find_one({"_id": user_guid}, {"passwordHash": 0, "passwordSalt": 0})

    def find_auth_user(self, username_or_email: str) -> dict[str, Any] | None:
        db = mongo_provider.get_database()
        if db is None:
            return None
        normalized = username_or_email.strip().lower()
        return db.users.find_one({"$or": [{"username": normalized}, {"email": normalized}]})

    def list_users(self) -> list[dict[str, Any]]:
        db = mongo_provider.get_database()
        if db is None:
            return []
        return list(db.users.find({}, {"passwordHash": 0, "passwordSalt": 0}).sort("name", 1))

    def create_user(self, document: dict[str, Any]) -> dict[str, Any]:
        db = mongo_provider.get_database()
        if db is None:
            raise RuntimeError("MongoDB is required for registration")
        db.users.insert_one(document)
        return db.users.find_one({"_id": document["_id"]}, {"passwordHash": 0, "passwordSalt": 0})

    def update_subscription(self, user_guid: str, subscription: str, billing_period: str | None = None) -> None:
        db = mongo_provider.get_database()
        if db is None:
            raise RuntimeError("MongoDB is required for subscription updates")
        db.users.update_one(
            {"_id": user_guid},
            {"$set": {"subscription": subscription, "billingPeriod": billing_period}},
        )


class KundliRepository:
    def find_kundli(self, user_id: str) -> dict[str, Any] | None:
        db = mongo_provider.get_database()
        if db is None:
            return None
        user = db.users.find_one({"id": user_id}, {"_id": 1})
        if user is None:
            return None
        return db.kundlis.find_one({"userRefId": user["_id"]}, {"_id": 0, "userRefId": 0})


class HoroscopeRepository:
    def find_horoscope(self, user_id: str) -> dict[str, Any] | None:
        db = mongo_provider.get_database()
        if db is None:
            return None
        user = db.users.find_one({"id": user_id}, {"_id": 1})
        if user is None:
            return None
        return db.horoscopes.find_one({"userRefId": user["_id"]}, {"_id": 0, "userRefId": 0})


class PanchangRepository:
    def find_panchang(self) -> dict[str, Any] | None:
        db = mongo_provider.get_database()
        if db is None:
            return None
        return db.panchangs.find_one(sort=[("date", -1)], projection={"_id": 0})
