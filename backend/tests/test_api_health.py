from fastapi.testclient import TestClient

from app.main import app

client=TestClient(app)

def test_health():
    r=client.get("/api/v1/health")
    assert r.status_code==200
    assert r.json()["success"]==True

def test_openapi():
    r=client.get("/api/v1/openapi.json")
    assert r.status_code==200
    assert "openapi" in r.json()

def test_crops():
    r=client.get("/api/v1/crops")
    assert r.status_code==200
    assert "success" in r.json()
