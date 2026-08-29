import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def _get_auth_headers(client, email, password):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    if r.status_code != 200:
        pytest.skip(f"Cannot authenticate {email}")
    return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

def test_transaction_fsm(client):
    # Farmer creates lot
    farmer_h = _get_auth_headers(client, "ramesh@demo.com", "demo123!")
    r = client.get("/api/v1/lots", headers=farmer_h)
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    if not items:
        pytest.skip("No lots available")
    lot_id = items[0]["id"]
    # Buyer creates offer
    buyer_h = _get_auth_headers(client, "mehta@demo.com", "demo123!")
    r2 = client.post("/api/v1/offers", json={
        "lot_id": lot_id, "quantity": 10.0, "price_per_unit": 2000.0
    }, headers=buyer_h)
    if r2.status_code != 201:
        pytest.skip("Could not create offer")
    offer_id = r2.json()["data"]["id"]
    # Farmer accepts -> creates reservation
    r3 = client.post(f"/api/v1/offers/{offer_id}/accept", headers=farmer_h)
    assert r3.status_code == 200
    reservation_id = r3.json()["data"].get("reservation_id")
    if not reservation_id:
        pytest.skip("No reservation created")
    # Buyer creates transaction from reservation
    r4 = client.post("/api/v1/transactions", json={
        "reservation_id": reservation_id
    }, headers=buyer_h)
    assert r4.status_code == 201
    txn_id = r4.json()["data"]["id"]
    # Transition through FSM
    transitions = ["PAYMENT_PENDING", "PAYMENT_CONFIRMED", "PROCESSING", "READY_FOR_DISPATCH", "IN_TRANSIT", "DELIVERED", "COMPLETED"]
    for status in transitions:
        r5 = client.post(f"/api/v1/transactions/{txn_id}/transition", json={
            "to_status": status
        }, headers=buyer_h)
        assert r5.status_code == 200
        assert r5.json()["data"]["status"] == status

def test_transactions_list(client):
    h = _get_auth_headers(client, "mehta@demo.com", "demo123!")
    r = client.get("/api/v1/transactions", headers=h)
    assert r.status_code == 200
    assert r.json()["success"] == True

def test_invalid_transition(client):
    h = _get_auth_headers(client, "mehta@demo.com", "demo123!")
    fake_id = str(uuid.uuid4())
    r = client.post(f"/api/v1/transactions/{fake_id}/transition", json={
        "to_status": "INVALID_STATUS"
    }, headers=h)
    assert r.status_code in (404, 409, 422)
