from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import StorageFacility

router = APIRouter(prefix="/storage", tags=["storage"])

@router.get("", response_model=dict)
def list_storage(request: Request, db: Session = Depends(get_db), page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    q=db.query(StorageFacility).filter(StorageFacility.status=="ACTIVE")
    total=q.count()
    items=q.offset((page-1)*limit).limit(limit).all()
    data=[{"id":str(s.id),"name":s.name,"type":s.type,"capacity":float(s.capacity) if s.capacity else None,"available_capacity":float(s.available_capacity) if s.available_capacity else None,"location_text":s.location_text,"cost_per_unit":float(s.cost_per_unit) if s.cost_per_unit else None} for s in items]
    return {"success":True,"data":{"items":data,"total":total,"page":page,"limit":limit,"pages":(total+limit-1)//limit},"message":f"{len(data)} facilities","request_id":getattr(request.state,"request_id",None)}
