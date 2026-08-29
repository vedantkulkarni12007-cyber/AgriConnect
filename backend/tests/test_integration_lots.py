import pytest
from fastapi.testclient import TestClient

def test_create_lot(client, auth_headers):
    r = client.post("/api/v1/lots", json={
        "crop": "Wheat", "grade": "A", "quantity": 100.0,
        "location_text": "Nashik Market", "district": "Nashik"
    }, headers=auth_headers)
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["public_id"].startswith("KL-LOT-")
    assert data["crop"] == "Wheat"
    assert data["grade"] == "A"

def test_list_lots(client):
    r = client.get("/api/v1/lots")
    assert r.status_code == 200
    assert r.json()["success"] == True
    assert "items" in r.json()["data"]

def test_get_lot(client):
    r = client.get("/api/v1/lots")
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    if items:
        lot_id = items[0]["id"]
        r2 = client.get(f"/api/v1/lots/{lot_id}")
        assert r2.status_code == 200
        assert r2.json()["success"] == True

def test_public_lot(client):
    r = client.get("/api/v1/lots")
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    if items:
        public_id = items[0]["public_id"]
        r2 = client.get(f"/api/v1/lots/public/{public_id}")
        assert r2.status_code == 200
        assert r2.json()["success"] == True
        assert r2.json()["data"]["public_id"] == public_id

def test_create_lot_unauthorized(client):
    r = client.post("/api/v1/lots", json={
        "crop": "Wheat", "grade": "A", "quantity": 100.0,
        "location_text": "Test", "district": "Test"
    })
    assert r.status_code == 401

def test_create_lot_duplicate_idempotency(client, auth_headers):
    headers = {**auth_headers, "Idempotency-Key": "dup-test-key-001"}
    r = client.post("/api/v1/lots", json={
        "crop": "Wheat", "grade": "A", "quantity": 100.0,
        "location_text": "Nashik", "district": "Nashik"
    }, headers=headers)
    assert r.status_code == 201
    r2 = client.post("/api/v1/lots", json={
        "crop": "Wheat", "grade": "A", "quantity": 100.0,
        "location_text": "Nashik", "district": "Nashik"
    }, headers=headers)
    assert r2.status_code == 201
    assert r.json()["data"]["public_id"] == r2.json()["data"]["public_id"]
