import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.rate_limit import rate_limit
from app.core.s3 import generate_presigned_url, get_s3_client, upload_file
from app.models import AuditLog, Dispute, Evidence, User
from app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/disputes", tags=["disputes"])

class CreateDisputeRequest(BaseModel):
    transaction_id: str | None = None
    reason: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5)
    category: str | None = "General Inquiry"
    priority: str | None = "MEDIUM"

class UpdateDisputeStatusRequest(BaseModel):
    status: str
    resolution: str | None = None

class EvidenceRequest(BaseModel):
    s3_key: str
    file_hash: str
    mime_type: str | None = None

@router.post("", response_model=dict, status_code=201)
@rate_limit(max_requests=15, window_seconds=60, key_prefix="rl_dispute")
def create_dispute(data: CreateDisputeRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    txn_id = None
    if data.transaction_id:
        try:
            txn_id = uuid.UUID(data.transaction_id)
        except (ValueError, TypeError):
            pass

    d = Dispute(
        id=uuid.uuid4(),
        transaction_id=txn_id,
        raised_by=user.id,
        reason=f"[{data.category or 'General'}] {data.reason}",
        description=data.description,
        status="OPEN"
    )
    db.add(d)

    rid = getattr(request.state, "request_id", str(uuid.uuid4()))
    db.add(
        AuditLog(
            actor_id=str(user.id),
            action="dispute.create",
            entity="disputes",
            entity_id=str(d.id),
            after={"reason": d.reason, "status": d.status},
            request_id=rid,
        )
    )

    # Notify admins/support
    NotificationService.create_notification(
        db=db,
        user_id=user.id,
        type_="support_ticket",
        title="Support Ticket Created",
        message=f"Your ticket '{data.reason}' (ID: #{str(d.id)[:8]}) has been received. Our team will review it.",
        related_id=d.id,
        outbox=True
    )

    db.commit()
    db.refresh(d)
    return {
        "success": True,
        "data": {
            "id": str(d.id),
            "reason": d.reason,
            "description": d.description,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        },
        "message": "Support ticket created successfully",
        "request_id": rid,
    }

@router.get("", response_model=dict)
def list_disputes(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Dispute)
    if user.role.lower() not in ("admin", "operator"):
        q = q.filter(Dispute.raised_by == user.id)
    items = q.order_by(Dispute.created_at.desc()).all()
    data = [
        {
            "id": str(d.id),
            "ticket_number": f"KL-TKT-{str(d.id)[:8].upper()}",
            "reason": d.reason,
            "description": d.description,
            "status": d.status,
            "resolution": d.resolution,
            "transaction_id": str(d.transaction_id) if d.transaction_id else None,
            "raised_by": str(d.raised_by),
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        }
        for d in items
    ]
    return {
        "success": True,
        "data": data,
        "message": f"{len(data)} support tickets",
        "request_id": getattr(request.state, "request_id", None),
    }

@router.get("/{dispute_id}", response_model=dict)
def get_dispute(dispute_id: str, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d = None
    try:
        u = uuid.UUID(dispute_id)
        d = db.query(Dispute).filter(Dispute.id == u).first()
    except (ValueError, TypeError):
        pass

    if not d:
        raise HTTPException(status_code=404, detail="Dispute or support ticket not found")

    # Authorize: ticket creator or admin
    if user.role.lower() not in ("admin", "operator") and d.raised_by != user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot access another user's support ticket")

    ev_items = db.query(Evidence).filter(Evidence.dispute_id == d.id).all()
    evidence_list = [
        {
            "id": str(ev.id),
            "filename": ev.s3_key.split("/")[-1],
            "s3_key": ev.s3_key,
            "mime_type": ev.mime_type,
            "url": generate_presigned_url(ev.s3_key) if get_s3_client() else None,
        }
        for ev in ev_items
    ]

    return {
        "success": True,
        "data": {
            "id": str(d.id),
            "ticket_number": f"KL-TKT-{str(d.id)[:8].upper()}",
            "reason": d.reason,
            "description": d.description,
            "status": d.status,
            "resolution": d.resolution,
            "transaction_id": str(d.transaction_id) if d.transaction_id else None,
            "evidence": evidence_list,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        },
        "message": "Ticket details",
        "request_id": getattr(request.state, "request_id", None),
    }

@router.post("/{dispute_id}/status", response_model=dict)
def update_dispute_status(dispute_id: str, data: UpdateDisputeStatusRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Restrict status changes to admin or operator
    if user.role.lower() not in ("admin", "operator"):
        raise HTTPException(status_code=403, detail="Forbidden: Only administrators can update dispute status")

    try:
        u = uuid.UUID(dispute_id)
        d = db.query(Dispute).filter(Dispute.id == u).first()
    except (ValueError, TypeError):
        d = None

    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")

    new_status = data.status.upper()
    d.status = new_status
    if data.resolution:
        d.resolution = data.resolution
    d.operator_id = user.id
    d.updated_at = datetime.now(timezone.utc)

    rid = getattr(request.state, "request_id", str(uuid.uuid4()))
    db.add(
        AuditLog(
            actor_id=str(user.id),
            action="dispute.update_status",
            entity="disputes",
            entity_id=str(d.id),
            after={"status": d.status, "resolution": d.resolution},
            request_id=rid,
        )
    )

    # Send persistent notification to ticket creator
    NotificationService.create_notification(
        db=db,
        user_id=d.raised_by,
        type_="support_update",
        title="Support Ticket Updated",
        message=f"Your ticket '{d.reason}' is now {new_status}. {data.resolution or ''}".strip(),
        related_id=d.id,
        outbox=True
    )

    db.commit()
    return {
        "success": True,
        "data": {"id": str(d.id), "status": d.status, "resolution": d.resolution},
        "message": f"Ticket status updated to {d.status}",
        "request_id": rid,
    }

ALLOWED_EVIDENCE_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "application/pdf",
}
MAX_EVIDENCE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

@router.post("/{dispute_id}/evidence", response_model=dict)
def add_evidence(dispute_id: str, data: EvidenceRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        u = uuid.UUID(dispute_id)
        d = db.query(Dispute).filter(Dispute.id == u).first()
    except (ValueError, TypeError):
        d = None

    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Authorize: dispute creator or admin/operator
    if user.role.lower() not in ("admin", "operator") and d.raised_by != user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot attach evidence to another user's dispute")

    ev = Evidence(id=uuid.uuid4(), dispute_id=d.id, uploader_id=user.id, s3_key=data.s3_key, file_hash=data.file_hash, mime_type=data.mime_type)
    db.add(ev)
    db.commit()
    return {"success": True, "data": {"id": str(ev.id)}, "message": "Evidence added", "request_id": getattr(request.state, "request_id", None)}

@router.post("/{dispute_id}/evidence/upload", response_model=dict)
async def upload_evidence(dispute_id: str, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        u = uuid.UUID(dispute_id)
        d = db.query(Dispute).filter(Dispute.id == u).first()
    except (ValueError, TypeError):
        d = None

    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Authorize: dispute creator or admin/operator
    if user.role.lower() not in ("admin", "operator") and d.raised_by != user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot upload evidence to another user's dispute")

    # Validate MIME type
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_EVIDENCE_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid file type '{content_type}'. Allowed types: PDF, JPEG, PNG, WEBP.")

    client = get_s3_client()
    if not client:
        raise HTTPException(status_code=503, detail="Storage service unavailable")

    import re
    safe_filename = re.sub(r"[^a-zA-Z0-9._-]", "_", file.filename or "evidence.jpg")
    key = f"disputes/{dispute_id}/{uuid.uuid4().hex[:8]}_{safe_filename}"
    try:
        content = await file.read()
        if len(content) > MAX_EVIDENCE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail=f"File exceeds maximum allowed size of {MAX_EVIDENCE_SIZE_BYTES // (1024 * 1024)}MB.")
        from io import BytesIO
        upload_file(BytesIO(content), key, content_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    import hashlib
    file_hash = hashlib.sha256(content).hexdigest()

    ev = Evidence(id=uuid.uuid4(), dispute_id=d.id, uploader_id=user.id, s3_key=key, file_hash=file_hash, mime_type=content_type)
    db.add(ev)
    db.commit()

    url = generate_presigned_url(key)
    return {"success": True, "data": {"id": str(ev.id), "s3_key": key, "url": url}, "message": "Evidence uploaded", "request_id": getattr(request.state, "request_id", None)}
