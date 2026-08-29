import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.idempotency import check_idempotency, save_idempotency
from app.models import AuditLog, Lot, OutboxEvent, Reservation, Transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])

ALLOWED_TRANSITIONS = {
    "CREATED": ["PAYMENT_PENDING","CANCELLED"],
    "PAYMENT_PENDING": ["PAYMENT_CONFIRMED","CANCELLED"],
    "PAYMENT_CONFIRMED": ["PROCESSING","DISPUTED"],
    "PROCESSING": ["READY_FOR_DISPATCH","DISPUTED"],
    "READY_FOR_DISPATCH": ["IN_TRANSIT","DISPUTED"],
    "IN_TRANSIT": ["DELIVERED","DISPUTED"],
    "DELIVERED": ["COMPLETED","DISPUTED"],
    "COMPLETED": [],
    "DISPUTED": ["RESOLVED","CANCELLED"],
    "CANCELLED": [],
}

class CreateTxnRequest(BaseModel):
    reservation_id: str

class TransitionRequest(BaseModel):
    to_status: str

@router.post("", response_model=dict, status_code=201)
def create_transaction(data: CreateTxnRequest, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cached=check_idempotency(request, db)
    if cached:
        return cached.response_body
    res=db.get(Reservation, data.reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if res.status != "ACTIVE":
        raise HTTPException(status_code=409, detail="Reservation not active")
    lot=db.get(Lot, res.lot_id)
    txn=Transaction(id=uuid.uuid4(), lot_id=res.lot_id, buyer_id=res.buyer_id, seller_id=lot.owner_id, allocation_id=None, offer_id=res.offer_id, status="CREATED", gross_value=float(res.quantity)*10, idempotency_key=request.headers.get("Idempotency-Key"))
    db.add(txn)
    res.status="CONSUMED"
    rid=getattr(request.state,"request_id",str(uuid.uuid4()))
    db.add(AuditLog(actor_id=str(user.id), action="transaction.create", entity="transactions", entity_id=str(txn.id), request_id=rid))
    db.add(OutboxEvent(aggregate="transactions", aggregate_id=str(txn.id), event_type="transaction.created", payload={"transaction_id":str(txn.id)}))
    db.commit()
    db.refresh(txn)
    body={"success":True,"data":{"id":str(txn.id),"status":txn.status,"lot_id":str(txn.lot_id)},"message":"Transaction created","request_id":rid}
    save_idempotency(request, db, 201, body)
    return body

@router.get("", response_model=dict)
def list_txns(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user), page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    q=db.query(Transaction)
    if user.role.lower()=="farmer":
        q=q.filter(Transaction.seller_id==user.id)
    elif user.role.lower()=="buyer":
        q=q.filter(Transaction.buyer_id==user.id)
    total=q.count()
    items=q.order_by(Transaction.created_at.desc()).offset((page-1)*limit).limit(limit).all()
    data=[{"id":str(t.id),"lot_id":str(t.lot_id),"status":t.status,"gross_value":float(t.gross_value) if t.gross_value else None} for t in items]
    return {"success":True,"data":{"items":data,"total":total,"page":page,"limit":limit,"pages":(total+limit-1)//limit},"message":f"{len(data)} transactions","request_id":getattr(request.state,"request_id",None)}

@router.get("/{txn_id}", response_model=dict)
def get_txn(txn_id: str, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t=db.get(Transaction, txn_id)
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"success":True,"data":{"id":str(t.id),"lot_id":str(t.lot_id),"buyer_id":str(t.buyer_id),"seller_id":str(t.seller_id),"status":t.status,"gross_value":float(t.gross_value) if t.gross_value else None},"message":"OK","request_id":getattr(request.state,"request_id",None)}

@router.post("/{txn_id}/transition", response_model=dict)
def transition(txn_id: str, data: TransitionRequest, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t=db.get(Transaction, txn_id)
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    cur=t.status
    nxt=data.to_status.upper()
    if nxt not in ALLOWED_TRANSITIONS.get(cur, []):
        raise HTTPException(status_code=409, detail=f"Invalid transition {cur} -> {nxt}")
    t.status=nxt
    db.add(AuditLog(actor_id=str(user.id), action=f"transaction.{nxt.lower()}", entity="transactions", entity_id=str(t.id), before={"status":cur}, after={"status":nxt}, request_id=getattr(request.state,"request_id",None)))
    db.commit()
    return {"success":True,"data":{"id":str(t.id),"status":t.status},"message":f"Transitioned to {nxt}","request_id":getattr(request.state,"request_id",None)}
