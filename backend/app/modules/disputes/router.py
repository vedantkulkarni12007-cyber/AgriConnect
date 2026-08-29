import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
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
    d=Dispute(id=uuid.uuid4(), transaction_id=uuid.UUID(data.transaction_id) if data.transaction_id else None, raised_by=user.id, reason=data.reason, description=data.description, status="OPEN")
    db.add(d)
    db.commit()
    db.refresh(d)
    return {"success":True,"data":{"id":str(d.id),"status":d.status},"message":"Dispute created","request_id":getattr(request.state,"request_id",None)}

@router.get("", response_model=dict)
def list_disputes(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q=db.query(Dispute)
    if user.role.lower() not in ("admin","operator"):
        q=q.filter(Dispute.raised_by==user.id)
    items=q.order_by(Dispute.created_at.desc()).all()
    data=[{"id":str(d.id),"reason":d.reason,"status":d.status,"description":d.description} for d in items]
    return {"success":True,"data":data,"message":f"{len(data)} disputes","request_id":getattr(request.state,"request_id",None)}

@router.post("/{dispute_id}/evidence", response_model=dict)
def add_evidence(dispute_id: str, data: EvidenceRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d=db.get(Dispute, dispute_id)
    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")
    ev=Evidence(id=uuid.uuid4(), dispute_id=d.id, uploader_id=user.id, s3_key=data.s3_key, file_hash=data.file_hash, mime_type=data.mime_type)
    db.add(ev)
    db.commit()
    return {"success":True,"data":{"id":str(ev.id)},"message":"Evidence added","request_id":getattr(request.state,"request_id",None)}
