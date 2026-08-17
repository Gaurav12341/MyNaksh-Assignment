from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.main import app
from app.models.context import SourceResult, UserContextBundle
from app.services.mocks.mock_data import HOROSCOPE, KUNDLI, PANCHANG, USER_PROFILES


def sample_bundle() -> UserContextBundle:
    return UserContextBundle(
        user=SourceResult(name="User Profile", data=USER_PROFILES["user_101"]),
        kundli=SourceResult(name="Kundli", data=KUNDLI["user_101"]),
        horoscope=SourceResult(name="Horoscope", data=HOROSCOPE["user_101"]),
        panchang=SourceResult(name="Panchang", data=PANCHANG),
    )


def test_debug_endpoint_returns_engine_plan(monkeypatch):
    async def fake_fetch_all(self, user_id, request_id=None, data_source="mock"):
        return sample_bundle()

    monkeypatch.setattr("app.services.context_fetcher.ContextFetcher.fetch_all", fake_fetch_all)
    app.dependency_overrides[get_current_user] = lambda: {"_id": "admin-guid", "id": "admin", "role": "admin"}
    client = TestClient(app)

    response = client.post(
        "/debug/personalization",
        json={
            "userId": "user_101",
            "question": "Should I consider changing my job this year?",
            "dataSource": "mock",
            "llmProvider": "mock",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "career"
    assert "Career Horoscope" in data["selectedContext"]
    assert "Relationship Horoscope" in data["excludedContext"]
    app.dependency_overrides.clear()


def test_personalize_endpoint_returns_required_shape(monkeypatch):
    async def fake_fetch_all(self, user_id, request_id=None, data_source="mock"):
        return sample_bundle()

    monkeypatch.setattr("app.services.context_fetcher.ContextFetcher.fetch_all", fake_fetch_all)
    app.dependency_overrides[get_current_user] = lambda: {"_id": "admin-guid", "id": "admin", "role": "admin"}
    client = TestClient(app)

    response = client.post(
        "/personalize",
        json={
            "userId": "user_101",
            "question": "Should I consider changing my job this year?",
            "dataSource": "mock",
            "llmProvider": "mock",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"answer", "confidence", "sourcesUsed"}
    assert data["confidence"] in {"HIGH", "MEDIUM", "LOW"}
    assert "Career Horoscope" in data["sourcesUsed"]
    app.dependency_overrides.clear()
