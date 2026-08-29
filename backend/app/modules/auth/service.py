import uuid

from fastapi import HTTPException, Request, status
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import AuditLog, OutboxEvent, User


def _geog(lat, lng):
    if lat is None or lng is None:
        return None
    return WKTElement(f"POINT({lng} {lat})", srid=4326, extended=True)


def register_user(db: Session, data, request: Request):
    if not data.email and not data.phone:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either phone number or email is required",
        )

    # Check for existing user
    if data.email:
        existing = db.query(User).filter(User.email == data.email.lower()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists. Please log in.",
            )
    if data.phone:
        existing = db.query(User).filter(User.phone == data.phone).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this phone number already exists. Please log in.",
            )

    uid = uuid.uuid4()
    latlng = {"Nashik": (19.9975, 73.7898), "Pune": (18.5204, 73.8567), "Mumbai": (19.0760, 72.8777)}.get(
        data.district or data.location or "Pune", (18.5204, 73.8567)
    )
    user = User(
        id=uid,
        email=data.email.lower() if data.email else None,
        phone=data.phone,
        full_name=data.full_name.strip(),
        password_hash=hash_password(data.password),
        role=data.role.lower(),
        location=data.location,
        district=data.district or data.location,
        state=data.state or "Maharashtra",
        location_geog=_geog(*latlng) if latlng else None,
        is_verified=False,
        is_active=True,
    )
    db.add(user)
    rid = getattr(request.state, "request_id", str(uuid.uuid4()))
    db.add(
        AuditLog(
            actor_id=str(uid),
            action="user.register",
            entity="users",
            entity_id=str(uid),
            after={"email": data.email, "role": data.role},
            request_id=rid,
        )
    )
    db.add(
        OutboxEvent(
            aggregate="users",
            aggregate_id=str(uid),
            event_type="user.registered",
            payload={"user_id": str(uid), "email": data.email, "role": data.role},
        )
    )
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email_or_phone: str, password: str, request: Request):
    login_id = email_or_phone.strip()
    user = (
        db.query(User)
        .filter((User.email == login_id.lower()) | (User.phone == login_id))
        .first()
    )
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/phone or password. Please check your credentials.",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated.")
    rid = getattr(request.state, "request_id", str(uuid.uuid4()))
    db.add(
        AuditLog(
            actor_id=str(user.id),
            action="user.login",
            entity="users",
            entity_id=str(user.id),
            after={"login": login_id},
            request_id=rid,
        )
    )
    db.commit()
    return user


def issue_tokens(user: User):
    access = create_access_token(str(user.id), user.role)
    refresh = create_refresh_token(str(user.id))
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_ttl_min * 60,
    }


def refresh_tokens(db: Session, refresh_token: str):
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    uid = payload.get("sub")
    try:
        user = db.get(User, uuid.UUID(uid))
    except Exception:
        user = None
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return issue_tokens(user)
