from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_verify():
    pw="demo12345"
    h=hash_password(pw)
    assert verify_password(pw, h)
    assert not verify_password("wrong", h)

def test_jwt():
    tok=create_access_token("user123","farmer")
    data=decode_token(tok)
    assert data["sub"]=="user123"
    assert data["role"]=="farmer"
    assert data["type"]=="access"
