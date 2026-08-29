import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.s3 import get_s3_client, upload_file, generate_presigned_url
from app.models import Dispute, Evidence, User

router = APIRouter(prefix="/disputes", tags=["disputes"])

class CreateDisputeRequest(BaseModel):
    transaction_id: str | None = None
    reason: str
    description: str

class EvidenceRequest(BaseModel):
    s3_key: str
    file_hash: str
    mime_type: str | None = None

@router.post("", response_model=dict, status_code=201)
def create_dispute(data: CreateDisputeRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d = Dispute(
        id=uuid.uuid4(),
        transaction_id=uuid.UUID(data.transaction_id) if data.transaction_id else None,
        raised_by=user.id,
        reason=data.reason,
        description=data.description,
        status="OPEN"
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return {"success": True, "data": {"id": str(d.id), "status": d.status}, "message": "Dispute created", "request_id": getattr(request.state, "request_id", None)}

@router.get("", response_model=dict)
def list_disputes(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Dispute)
    if user.role.lower() not in ("admin", "operator"):
        q = q.filter(Dispute.raised_by == user.id)
    items = q.order_by(Dispute.created_at.desc()).all()
    data = [{"id": str(d.id), "reason": d.reason, "status": d.status, "description": d.description} for d in items]
    return {"success": True, "data": data, "message": f"{len(data)} disputes", "request_id": getattr(request.state, "request_id", None)}

@router.post("/{dispute_id}/evidence", response_model=dict)
def add_evidence(dispute_id: str, data: EvidenceRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d = db.get(Dispute, dispute_id)
    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")
    ev = Evidence(id=uuid.uuid4(), dispute_id=d.id, uploader_id=user.id, s3_key=data.s3_key, file_hash=data.file_hash, mime_type=data.mime_type)
    db.add(ev)
    db.commit()
    return {"success": True, "data": {"id": str(ev.id)}, "message": "Evidence added", "request_id": getattr(request.state, "request_id", None)}

@router.post("/{dispute_id}/evidence/upload", response_model=dict)
async def upload_evidence(dispute_id: str, file: UploadFile = File(...), request: Request = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d = db.get(Dispute, dispute_id)
    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")
    
    client = get_s3_client()
    if not client:
        raise HTTPException(status_code=503, detail="S3 storage not configured")
    
    key = f"disputes/{dispute_id}/{uuid.uuid4().hex[:8]}_{file.filename}"
    try:
        content = await file.read()
        from io import BytesIO
        upload_file(BytesIO(content), key, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")
    
    import hashlib
    file_hash = hashlib.sha256(content).hexdigest()
    
    ev = Evidence(id=uuid.uuid4(), dispute_id=d.id, uploader_id=user.id, s3_key=key, file_hash=file_hash, mime_type=file.content_type)
    db.add(ev)
    db.commit()
    
    url = generate_presigned_url(key)
    return {"success": True, "data": {"id": str(ev.id), "s3_key": key, "url": url}, "message": "Evidence uploaded", "request_id": getattr(request.state, "request_id", None)}

@router.get("/{dispute_id}/evidence/{evidence_id}/download", response_model=dict)
def download_evidence(dispute_id: str, evidence_id: str, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ev = db.get(Evidence, evidence_id)
    if not ev or str(ev.dispute_id) != dispute_id:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    client = get_s3_client()
    if not client:
        raise HTTPException(status_code=503, detail="S3 storage not configured")
    
    url = generate_presigned_url(ev.s3_key)
    return {"success": True, "data": {"url": url, "filename": ev.s3_key.split("/")[-1]}, "message": "Download URL generated", "request_id": getattr(request.state, "request_id", None)}