from fastapi import APIRouter, Depends, Request

from app.core.deps import get_current_user, require_role
from app.models import User
from app.modules.auth.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=dict)
def get_me(request: Request, user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": UserResponse.model_validate(user).model_dump(),
        "request_id": getattr(request.state, "request_id", None),
    }


@router.get("/admin-only", response_model=dict)
def admin_only(user: User = Depends(require_role("admin"))):
    return {"success": True, "data": {"message": f"Hello admin {user.full_name}"}, "request_id": None}
