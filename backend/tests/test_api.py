import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import init_db
from app.models.user import User

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()
    yield

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_auth_and_flow():
    # 1. Register new user
    reg_res = client.post("/api/v1/auth/register", json={
        "email": "tester@code2026.com",
        "password": "testpassword123",
        "full_name": "Test Trader",
        "persona_level": "intermediate"
    })
    assert reg_res.status_code in [200, 400]
    
    # 2. Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": "tester@code2026.com",
        "password": "testpassword123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Add to Watchlist
    watchlist_res = client.get("/api/v1/watchlist", headers=headers)
    assert watchlist_res.status_code == 200
    if not watchlist_res.json():
        add_res = client.post("/api/v1/watchlist", json={"symbol": "NVDA"}, headers=headers)
        assert add_res.status_code == 200
        watchlist_res = client.get("/api/v1/watchlist", headers=headers)
    watched_symbol = watchlist_res.json()[0]["symbol"]

    # 4. Search stocks
    search_res = client.get("/api/v1/watchlist/search?q=NVD")
    assert search_res.status_code == 200
    assert len(search_res.json()) > 0

    # 5. Simulate 4 hours away with divergence
    sim_res = client.post("/api/v1/memory/simulate-away", json={
        "minutes_away": 263,
        "scenario": "tech_divergence"
    }, headers=headers)
    assert sim_res.status_code == 200
    assert sim_res.json()["trigger_type"] == "simulated"

    # 6. Fetch "While You Were Away" feed
    feed_res = client.get("/api/v1/feed/while-you-were-away", headers=headers)
    assert feed_res.status_code == 200
    feed_data = feed_res.json()
    assert "elapsed_human" in feed_data
    assert "market_story_headline" in feed_data
    assert "market_story_summary" in feed_data
    assert isinstance(feed_data["meaningful_stocks"], list)
    assert isinstance(feed_data["normal_stocks"], list)

    # 7. Test "Why Wasn't I Alerted?" endpoint
    proof_res = client.get(f"/api/v1/stocks/{watched_symbol}/why-not-alerted", headers=headers)
    assert proof_res.status_code == 200
    proof_data = proof_res.json()
    assert proof_data["symbol"] == watched_symbol
    assert "reasons" in proof_data
    assert "verdict" in proof_data

    # 8. Test Persona Re-explanation
    explain_res = client.post("/api/v1/explain/re-explain", json={
        "persona": "beginner",
        "language": "en",
        "elapsed_time_human": "4h 23m",
        "flagged_stocks": [
            {
                "symbol": "NVDA",
                "delta_pct": 6.1,
                "attention_score": 86,
                "factors": {
                    "volume_anomaly": {"raw_value": 2.8},
                    "volatility_z_score": {"raw_value": 3.2}
                }
            }
        ]
    }, headers=headers)
    assert explain_res.status_code == 200
    exp_data = explain_res.json()
    assert "story_headline" in exp_data
    assert len(exp_data["stock_explanations"]) == 1

def test_invalid_login_and_watchlist_isolation():
    run_id = uuid.uuid4().hex
    user_a = client.post("/api/v1/auth/register", json={
        "email": f"isolation-a-{run_id}@marketpulse.test",
        "password": "password123",
    }).json()
    user_b = client.post("/api/v1/auth/register", json={
        "email": f"isolation-b-{run_id}@marketpulse.test",
        "password": "password123",
    }).json()
    headers_a = {"Authorization": f"Bearer {user_a['access_token']}"}
    headers_b = {"Authorization": f"Bearer {user_b['access_token']}"}

    assert client.post("/api/v1/auth/login", json={
        "email": f"isolation-a-{run_id}@marketpulse.test",
        "password": "wrong-password",
    }).status_code == 401
    assert client.post("/api/v1/watchlist", json={"symbol": "TCS"}, headers=headers_a).status_code == 200
    assert client.get("/api/v1/watchlist", headers=headers_b).json() == []
    assert client.get("/api/v1/stocks/TCS/why-not-alerted", headers=headers_b).status_code == 404

def test_registration_rejects_invalid_persona_and_weak_password():
    response = client.post("/api/v1/auth/register", json={
        "email": "invalid@marketpulse.test",
        "password": "weak",
        "persona_level": "judge",
    })
    assert response.status_code == 422
