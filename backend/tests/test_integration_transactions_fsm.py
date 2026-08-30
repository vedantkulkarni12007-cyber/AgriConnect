import uuid

def test_transaction_fsm(client, auth_headers, buyer_auth_headers):
    # Ensure lot exists
    r = client.get("/api/v1/lots", headers=auth_headers)
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    if not items:
        r_lot = client.post("/api/v1/lots", json={
            "crop": "Wheat", "grade": "A", "quantity": 100.0,
            "location_text": "Nashik Market", "district": "Nashik"
        }, headers=auth_headers)
        assert r_lot.status_code == 201
        lot_id = r_lot.json()["data"]["id"]
    else:
        lot_id = items[0]["id"]

    # Buyer creates offer
    r2 = client.post("/api/v1/offers", json={
        "lot_id": lot_id, "quantity": 10.0, "price_per_unit": 2000.0
    }, headers=buyer_auth_headers)
    assert r2.status_code == 201
    offer_id = r2.json()["data"]["id"]

    # Farmer accepts -> creates reservation
    r3 = client.post(f"/api/v1/offers/{offer_id}/accept", headers=auth_headers)
    assert r3.status_code == 200
    reservation_id = r3.json()["data"]["reservation_id"]
    assert reservation_id is not None

    # Buyer creates transaction from reservation
    r4 = client.post("/api/v1/transactions", json={
        "reservation_id": reservation_id
    }, headers=buyer_auth_headers)
    assert r4.status_code == 201
    txn_id = r4.json()["data"]["id"]

    # Transition through FSM
    transitions = ["PAYMENT_PENDING", "PAYMENT_CONFIRMED", "PROCESSING", "READY_FOR_DISPATCH", "IN_TRANSIT", "DELIVERED", "COMPLETED"]
    for status in transitions:
        r5 = client.post(f"/api/v1/transactions/{txn_id}/transition", json={
            "to_status": status
        }, headers=buyer_auth_headers)
        assert r5.status_code == 200
        assert r5.json()["data"]["status"] == status

def test_transactions_list(client, buyer_auth_headers):
    r = client.get("/api/v1/transactions", headers=buyer_auth_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True

def test_invalid_transition(client, buyer_auth_headers):
    fake_id = str(uuid.uuid4())
    r = client.post(f"/api/v1/transactions/{fake_id}/transition", json={
        "to_status": "INVALID_STATUS"
    }, headers=buyer_auth_headers)
    assert r.status_code in (404, 409, 422)
