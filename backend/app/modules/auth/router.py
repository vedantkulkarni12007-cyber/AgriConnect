from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.modules.auth.schemas import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, UserResponse
from app.modules.auth.service import register_user, authenticate_user, issue_tokens, refresh_tokens

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=dict, status_code=201)
def register(data: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    user = register_user(db, data, request)
    tokens = issue_tokens(user)
    return {"success": True, "data": {"user": UserResponse.model_validate(user).model_dump(), **tokens}, "message": "Registered successfully", "request_id": getattr(request.state, "request_id", None)}

@router.post("/login", response_model=dict)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password, request)
    tokens = issue_tokens(user)
    return {"success": True, "data": {"user": UserResponse.model_validate(user).model_dump(), **tokens}, "message": "Login successful", "request_id": getattr(request.state, "request_id", None)}

@router.post("/refresh", response_model=dict)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    tokens = refresh_tokens(db, data.refresh_token)
    return {"success": True, "data": tokens, "message": "Tokens refreshed", "request_id": None}

@router.get("/me", response_model=dict)
def me(request: Request, user: User = Depends(get_current_user)):
    return {"success": True, "data": UserResponse.model_validate(user).model_dump(), "message": "Current user", "request_id": getattr(request.state, "request_id", None)}

@router.post("/logout", response_model=dict)
def logout(request: Request, user: User = Depends(get_current_user)):
    return {"success": True, "data": None, "message": "Logged out (client should discard tokens)", "request_id": getattr(request.state, "request_id", None)}
