import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session", autouse=True)
def ensure_test_users():
    db = SessionLocal()
    try:
        users_to_ensure = [
            ("ramesh@demo.com", "9876543210", "Ramesh Patil", "farmer", "Nashik, Maharashtra", "Nashik"),
            ("buyer@demo.com", "9876543211", "Sunil Mehta", "buyer", "Mumbai, Maharashtra", "Mumbai"),
            ("mehta@demo.com", "9876543212", "Mehta Traders", "buyer", "Nashik, Maharashtra", "Nashik"),
            ("admin@demo.com", "9876543213", "Admin User", "admin", "Mumbai, Maharashtra", "Mumbai"),
            ("fpo@demo.com", "9876543214", "Nashik Farmers Collective", "fpo", "Nashik, Maharashtra", "Nashik"),
        ]
        
        for email, phone, name, role, loc, dist in users_to_ensure:
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(
                    id=uuid.uuid4(),
                    email=email,
                    phone=phone,
                    full_name=name,
                    password_hash=hash_password("demo123!"),
                    role=role,
                    location=loc,
                    district=dist,
                    state="Maharashtra",
                    is_verified=True,
                    is_active=True
                )
                db.add(u)
            else:
                u.password_hash = hash_password("demo123!")
                u.is_active = True
                
        db.commit()
    finally:
        db.close()

@pytest.fixture
def auth_headers(client, ensure_test_users):
    r = client.post("/api/v1/auth/login", json={"email": "ramesh@demo.com", "password": "demo123!"})
    if r.status_code != 200:
        pytest.fail(f"Cannot authenticate test farmer user: {r.text}")
    data = r.json()["data"]
    return {"Authorization": f"Bearer {data['access_token']}"}

@pytest.fixture
def buyer_auth_headers(client, ensure_test_users):
    r = client.post("/api/v1/auth/login", json={"email": "buyer@demo.com", "password": "demo123!"})
    if r.status_code != 200:
        pytest.fail(f"Cannot authenticate test buyer user: {r.text}")
    data = r.json()["data"]
    return {"Authorization": f"Bearer {data['access_token']}"}

@pytest.fixture
def admin_auth_headers(client, ensure_test_users):
    r = client.post("/api/v1/auth/login", json={"email": "admin@demo.com", "password": "demo123!"})
    if r.status_code != 200:
        pytest.fail(f"Cannot authenticate test admin user: {r.text}")
    data = r.json()["data"]
    return {"Authorization": f"Bearer {data['access_token']}"}