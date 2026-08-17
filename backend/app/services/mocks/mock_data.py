MOCK_USERS = [
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


def build_user_profiles():
    profiles = {}
    for user_id, name, language, subscription, tone, birth_date, birth_time, place, *_ in MOCK_USERS:
        profiles[user_id] = {
            "id": user_id,
            "name": name,
            "language": language,
            "subscription": subscription,
            "tonePreference": tone,
            "birthDetails": {
                "date": birth_date,
                "time": birth_time,
                "place": place,
            },
        }
    return profiles


def build_kundlis():
    kundlis = {}
    for index, item in enumerate(MOCK_USERS, start=1):
        user_id, *_prefix, lagna, moon, maha, antar = item
        kundlis[user_id] = {
            "lagna": lagna,
            "moonSign": moon,
            "currentDasha": {
                "mahadasha": maha,
                "antardasha": antar,
            },
            "houses": {
                "6": {
                    "lord": ["Jupiter", "Mercury", "Saturn"][index % 3],
                    "strength": ["Average", "Strong", "Weak"][index % 3],
                },
                "7": {
                    "lord": ["Mars", "Moon", "Venus"][index % 3],
                    "strength": ["Weak", "Average", "Strong"][index % 3],
                },
                "10": {
                    "lord": ["Moon", "Venus", "Saturn"][index % 3],
                    "strength": ["Strong", "Average", "Weak"][index % 3],
                },
            },
        }
    return kundlis


def build_horoscopes():
    horoscopes = {}
    for item in MOCK_USERS:
        user_id, name, *_ = item
        first_name = name.split()[0]
        horoscopes[user_id] = {
            "career": f"{first_name} may benefit from focused networking and clearer professional priorities.",
            "finance": "Review commitments carefully and avoid impulsive financial decisions.",
            "health": "Steady rest, hydration, and routine will support better energy.",
            "relationship": "Patient communication can make emotional exchanges smoother.",
            "general": "A measured approach will work better than scattering attention.",
        }
    return horoscopes


USER_PROFILES = build_user_profiles()
KUNDLI = build_kundlis()
HOROSCOPE = build_horoscopes()

PANCHANG = {
    "date": "2026-08-17",
    "tithi": "Shukla Panchami",
    "nakshatra": "Rohini",
    "yoga": "Siddhi",
    "karana": "Bava",
}
