import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_headers(client):
    r = client.post("/api/v1/auth/login", json={"email": "ramesh@demo.com", "password": "demo123!"})
    if r.status_code != 200:
        pytest.skip("Cannot authenticate test user")
    data = r.json()["data"]
    return {"Authorization": f"Bearer {data['access_token']}"}