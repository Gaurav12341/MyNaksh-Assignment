from __future__ import annotations

from datetime import date
import os
from pathlib import Path
import sys
from uuid import uuid5, NAMESPACE_DNS

from pymongo import MongoClient, ReplaceOne

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


USERS = [
    ("user_101", "Aarav Sharma", "en", "premium", "motivational", "1997-08-15", "09:35", "Delhi", "Libra", "Scorpio", "Rahu", "Mars"),
    ("user_102", "Meera Iyer", "en", "free", "practical", "1992-02-20", "21:10", "Mumbai", "Capricorn", "Taurus", "Saturn", "Venus"),
    ("user_103", "Kabir Malhotra", "en", "premium", "calm", "1989-11-03", "06:45", "Jaipur", "Leo", "Cancer", "Jupiter", "Mercury"),
    ("user_104", "Ananya Rao", "en", "free", "motivational", "1995-04-12", "14:05", "Bengaluru", "Virgo", "Gemini", "Venus", "Saturn"),
    ("user_105", "Rohan Gupta", "en", "premium", "practical", "1990-09-28", "18:20", "Pune", "Sagittarius", "Aries", "Mars", "Rahu"),
    ("user_106", "Ishita Sen", "en", "free", "calm", "1999-01-07", "03:15", "Kolkata", "Pisces", "Aquarius", "Moon", "Jupiter"),
    ("user_107", "Dev Patel", "en", "premium", "concise", "1987-06-18", "11:55", "Ahmedabad", "Taurus", "Libra", "Mercury", "Ketu"),
    ("user_108", "Nisha Verma", "en", "free", "motivational", "1994-12-01", "23:40", "Lucknow", "Cancer", "Virgo", "Sun", "Moon"),
    ("user_109", "Arjun Menon", "en", "premium", "practical", "1991-07-24", "08:25", "Kochi", "Aries", "Sagittarius", "Ketu", "Venus"),
    ("user_110", "Priya Nair", "en", "free", "calm", "1998-10-30", "16:50", "Chennai", "Gemini", "Pisces", "Venus", "Mars"),
]

DEFAULT_PASSWORD = "Password@123"
ADMIN_PASSWORD = "Admin@12345"


def guid_for(value: str) -> str:
    return str(uuid5(NAMESPACE_DNS, f"mynaksh-poc:{value}"))


def build_documents():
    user_docs = []
    kundli_docs = []
    horoscope_docs = []
    for index, item in enumerate(USERS, start=1):
        user_id, name, language, subscription, tone, birth_date, birth_time, place, lagna, moon, maha, antar = item
        user_guid = guid_for(user_id)
        password_hash, password_salt = hash_password(DEFAULT_PASSWORD)
        user_docs.append(
            {
                "_id": user_guid,
                "id": user_id,
                "name": name,
                "username": user_id,
                "email": f"{user_id}@mynaksh.local",
                "passwordHash": password_hash,
                "passwordSalt": password_salt,
                "role": "user",
                "language": language,
                "subscription": subscription,
                "billingPeriod": "monthly" if subscription == "premium" else None,
                "tonePreference": tone,
                "birthDetails": {"date": birth_date, "time": birth_time, "place": place},
            }
        )
        kundli_docs.append(
            {
                "_id": guid_for(f"kundli:{user_id}"),
                "userRefId": user_guid,
                "lagna": lagna,
                "moonSign": moon,
                "currentDasha": {"mahadasha": maha, "antardasha": antar},
                "houses": {
                    "6": {"lord": ["Jupiter", "Mercury", "Saturn"][index % 3], "strength": ["Average", "Strong", "Weak"][index % 3]},
                    "7": {"lord": ["Mars", "Moon", "Venus"][index % 3], "strength": ["Weak", "Average", "Strong"][index % 3]},
                    "10": {"lord": ["Moon", "Venus", "Saturn"][index % 3], "strength": ["Strong", "Average", "Weak"][index % 3]},
                },
            }
        )
        horoscope_docs.append(
            {
                "_id": guid_for(f"horoscope:{user_id}"),
                "userRefId": user_guid,
                "career": f"{name.split()[0]} may benefit from focused networking and clearer professional priorities.",
                "finance": "Review commitments carefully and avoid impulsive financial decisions.",
                "health": "Steady rest, hydration, and routine will support better energy.",
                "relationship": "Patient communication can make emotional exchanges smoother.",
                "general": "A measured approach will work better than scattering attention.",
            }
        )

    panchang_docs = [
        {
            "_id": guid_for(f"panchang:{date.today().isoformat()}"),
            "date": date.today().isoformat(),
            "tithi": "Shukla Panchami",
            "nakshatra": "Rohini",
            "yoga": "Siddhi",
            "karana": "Bava",
        }
    ]
    admin_hash, admin_salt = hash_password(ADMIN_PASSWORD)
    user_docs.append(
        {
            "_id": guid_for("admin"),
            "id": "admin",
            "name": "Master Admin",
            "username": "admin",
            "email": "admin@mynaksh.local",
            "passwordHash": admin_hash,
            "passwordSalt": admin_salt,
            "role": "admin",
            "language": "en",
            "subscription": "premium",
            "billingPeriod": "yearly",
            "tonePreference": "practical",
            "birthDetails": {"date": "1990-01-01", "time": "00:00", "place": "Delhi"},
        }
    )
    return user_docs, kundli_docs, horoscope_docs, panchang_docs


def main() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    load_dotenv(backend_root / ".env")
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.getenv("MONGO_DATABASE", "mynaksh_poc")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    db = client[database_name]

    users, kundlis, horoscopes, panchangs = build_documents()
    db.users.drop()
    db.kundlis.drop()
    db.horoscopes.drop()
    db.panchangs.drop()

    db.users.create_index("id", unique=True)
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True)
    db.kundlis.create_index("userRefId", unique=True)
    db.horoscopes.create_index("userRefId", unique=True)
    db.panchangs.create_index("date", unique=True)
    db.users.bulk_write([ReplaceOne({"_id": doc["_id"]}, doc, upsert=True) for doc in users])
    db.kundlis.bulk_write([ReplaceOne({"_id": doc["_id"]}, doc, upsert=True) for doc in kundlis])
    db.horoscopes.bulk_write([ReplaceOne({"_id": doc["_id"]}, doc, upsert=True) for doc in horoscopes])
    db.panchangs.bulk_write([ReplaceOne({"_id": doc["_id"]}, doc, upsert=True) for doc in panchangs])

    print(f"Seeded {database_name}: users={len(users)}, kundlis={len(kundlis)}, horoscopes={len(horoscopes)}, panchangs={len(panchangs)}")


if __name__ == "__main__":
    main()
