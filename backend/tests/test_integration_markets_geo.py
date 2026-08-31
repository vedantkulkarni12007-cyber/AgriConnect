import pytest


def test_list_markets(client):
    r = client.get("/api/v1/markets")
    assert r.status_code == 200
    res = r.json()
    assert res["success"] is True
    assert "items" in res["data"]
    assert isinstance(res["data"]["items"], list)


def test_list_markets_proximity_search(client):
    # Proximity search near Nashik coordinates
    r = client.get("/api/v1/markets?near_lat=19.9975&near_lng=73.7898&radius_km=100")
    assert r.status_code == 200
    res = r.json()
    assert res["success"] is True
    items = res["data"]["items"]
    assert isinstance(items, list)
    if items:
        # Distance should be calculated
        assert "distance_km" in items[0]


def test_map_locations_endpoint(client):
    r = client.get("/api/v1/markets/locations?category=all")
    assert r.status_code == 200
    res = r.json()
    assert res["success"] is True
    data = res["data"]
    assert "locations" in data
    assert "counts" in data
    assert isinstance(data["locations"], list)


def test_live_mandi_prices_endpoint(client):
    r = client.get("/api/v1/prices/live?crop=Onion&limit=10")
    assert r.status_code == 200
    res = r.json()
    assert res["success"] is True
    assert "data" in res
    assert "items" in res["data"]
    assert isinstance(res["data"]["items"], list)


def test_price_trends_endpoint(client):
    r = client.get("/api/v1/prices/trends/Onion")
    assert r.status_code == 200
    res = r.json()
    assert res["success"] is True
    assert "data" in res
    assert "trend" in res["data"]
