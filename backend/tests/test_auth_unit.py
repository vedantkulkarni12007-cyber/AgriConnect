import pytest
import jwt
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

def test_hash_verify():
    pw = "demo12345"
    h = hash_password(pw)
    assert verify_password(pw, h)
    assert not verify_password("wrong", h)

def test_jwt_access():
    tok = create_access_token("user123", "farmer")
    data = decode_token(tok)
    assert data["sub"] == "user123"
    assert data["role"] == "farmer"
    assert data["type"] == "access"
    assert "jti" in data

def test_jwt_refresh():
    tok = create_refresh_token("user123")
    data = decode_token(tok)
    assert data["sub"] == "user123"
    assert data["type"] == "refresh"
    assert "jti" in data

def test_jwt_expired():
    import time
    import jwt
    from app.core.config import settings
    
    # Create an expired token manually
    expired = jwt.encode(
        {"sub": "user123", "role": "farmer", "type": "access", "exp": 1},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(expired)

def test_jwt_invalid():
    with pytest.raises(jwt.InvalidTokenError):
        decode_token("invalid.token.here")