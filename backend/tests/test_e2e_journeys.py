import pytest

# ==============================================================================
# Multi-Role End-to-End Journey Tests (KrishiLink 2.0 Phase 9)
# ==============================================================================

def test_farmer_end_to_end_journey(client, auth_headers):
    # 1. Farmer checks current profile
    r_me = client.get("/api/v1/auth/me", headers=auth_headers)
    assert r_me.status_code == 200
    assert r_me.json()["data"]["role"] == "farmer"

    # 2. Farmer lists a new produce lot
    lot_payload = {
        "crop": "Tomato",
        "grade": "A",
        "quantity": 150.0,
        "asking_price": 1400.0,
        "location_text": "Nashik APMC Mandi",
        "district": "Nashik"
    }
    r_lot = client.post("/api/v1/lots", json=lot_payload, headers=auth_headers)
    assert r_lot.status_code == 201
    lot_data = r_lot.json()["data"]
    lot_id = lot_data["id"]
    assert lot_data["public_id"].startswith("KL-LOT-")

    # 3. Farmer checks matches for the lot
    r_match = client.post("/api/v1/matches/refresh", json={"lot_id": lot_id}, headers=auth_headers)
    assert r_match.status_code == 200
    assert isinstance(r_match.json()["data"], list)

    # 4. Farmer files a support ticket / grievance
    dispute_payload = {
        "reason": "Grading certificate delay",
        "description": "Quality grading report from APMC inspector is delayed by 24 hours.",
        "category": "Listing Accuracy",
        "priority": "MEDIUM"
    }
    r_disp = client.post("/api/v1/disputes", json=dispute_payload, headers=auth_headers)
    assert r_disp.status_code == 201
    assert r_disp.json()["data"]["status"] == "OPEN"

    # 5. Farmer views their notifications
    r_notif = client.get("/api/v1/notifications", headers=auth_headers)
    assert r_notif.status_code == 200
    assert "items" in r_notif.json()["data"]


def test_buyer_end_to_end_journey(client, auth_headers, buyer_auth_headers):
    # 1. Farmer lists produce
    lot_payload = {
        "crop": "Soybean",
        "grade": "A",
        "quantity": 200.0,
        "asking_price": 4200.0,
        "location_text": "Solapur Mandi",
        "district": "Solapur"
    }
    r_lot = client.post("/api/v1/lots", json=lot_payload, headers=auth_headers)
    assert r_lot.status_code == 201
    lot_id = r_lot.json()["data"]["id"]

    # 2. Buyer discovers produce lots in marketplace
    r_browse = client.get("/api/v1/lots", headers=buyer_auth_headers)
    assert r_browse.status_code == 200
    items = r_browse.json()["data"]["items"]
    assert len(items) > 0

    # 3. Buyer makes an offer on the lot
    offer_payload = {
        "lot_id": lot_id,
        "quantity": 100.0,
        "price_per_unit": 4150.0,
        "message": "Immediate pickup via Solapur logistics depot"
    }
    r_offer = client.post("/api/v1/offers", json=offer_payload, headers=buyer_auth_headers)
    assert r_offer.status_code == 201
    offer_id = r_offer.json()["data"]["id"]

    # 4. Farmer accepts the buyer's offer
    r_accept = client.post(f"/api/v1/offers/{offer_id}/accept", headers=auth_headers)
    assert r_accept.status_code == 200
    res_id = r_accept.json()["data"]["reservation_id"]
    assert res_id is not None

    # 5. Buyer creates transaction from reservation
    r_txn = client.post("/api/v1/transactions", json={"reservation_id": res_id}, headers=buyer_auth_headers)
    assert r_txn.status_code == 201
    txn_id = r_txn.json()["data"]["id"]

    # 6. Escrow state transitions
    r_trans1 = client.post(f"/api/v1/transactions/{txn_id}/transition", json={"to_status": "PAYMENT_PENDING"}, headers=buyer_auth_headers)
    assert r_trans1.status_code == 200

    r_trans2 = client.post(f"/api/v1/transactions/{txn_id}/transition", json={"to_status": "PAYMENT_CONFIRMED"}, headers=buyer_auth_headers)
    assert r_trans2.status_code == 200


def test_fpo_end_to_end_journey(client):
    # 1. Login as FPO
    r_login = client.post("/api/v1/auth/login", json={"email": "fpo@demo.com", "password": "demo123!"})
    assert r_login.status_code == 200
    token = r_login.json()["data"]["access_token"]
    fpo_headers = {"Authorization": f"Bearer {token}"}

    # 2. FPO lists aggregated lot
    agg_payload = {
        "crop": "Wheat",
        "grade": "A",
        "quantity": 500.0,
        "asking_price": 2300.0,
        "location_text": "Nashik Collective Warehouse",
        "district": "Nashik"
    }
    r_lot = client.post("/api/v1/lots", json=agg_payload, headers=fpo_headers)
    assert r_lot.status_code == 201

    # 3. FPO checks verified storage facilities
    r_storage = client.get("/api/v1/storage", headers=fpo_headers)
    assert r_storage.status_code == 200
    assert "items" in r_storage.json()["data"]


def test_admin_end_to_end_journey(client, auth_headers, admin_auth_headers):
    # 1. Farmer raises dispute
    disp = client.post("/api/v1/disputes", json={
        "reason": "Transit temperature issue",
        "description": "Temperature exceeded cold-storage threshold during transit.",
        "category": "Delivery & Transport"
    }, headers=auth_headers)
    assert disp.status_code == 201
    dispute_id = disp.json()["data"]["id"]

    # 2. Admin inspects all disputes
    r_list = client.get("/api/v1/disputes", headers=admin_auth_headers)
    assert r_list.status_code == 200

    # 3. Admin updates dispute resolution status
    r_resolve = client.post(f"/api/v1/disputes/{dispute_id}/status", json={
        "status": "RESOLVED",
        "resolution": "Compensation approved via logistics insurance policy."
    }, headers=admin_auth_headers)
    assert r_resolve.status_code == 200
    assert r_resolve.json()["data"]["status"] == "RESOLVED"

    # 4. Admin inspects system health and users
    r_health = client.get("/api/v1/admin/system-health", headers=admin_auth_headers)
    assert r_health.status_code == 200
    assert "checks" in r_health.json()["data"]

    r_users = client.get("/api/v1/admin/users", headers=admin_auth_headers)
    assert r_users.status_code == 200
    assert len(r_users.json()["data"]["items"]) > 0

    r_audit = client.get("/api/v1/admin/audit", headers=admin_auth_headers)
    assert r_audit.status_code == 200

    # 5. Admin checks outbox
    r_outbox = client.get("/api/v1/notifications/outbox/pending", headers=admin_auth_headers)
    assert r_outbox.status_code == 200
