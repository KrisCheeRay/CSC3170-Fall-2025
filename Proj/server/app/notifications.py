from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from .deps import get_db, get_current
from .models import Notification
from .schemas import NotificationOut, NotificationReadIn

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=list[NotificationOut])
def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    
    visitor_id = None
    if me["role"] == "visitor":
        visitor_id = int(me["sub"])
    else:
        
        raise HTTPException(403, "Only visitor can view notifications")

    q = db.query(Notification).filter(Notification.visitor_id == visitor_id)
    if unread_only:
        q = q.filter(Notification.is_read == 0)
    q = q.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
    return q.all()

@router.get("/unread_count")
def unread_count(
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    if me["role"] != "visitor":
        raise HTTPException(403, "Only visitor can view unread count")
    count = db.query(Notification).filter(
        Notification.visitor_id == int(me["sub"]),
        Notification.is_read == 0
    ).count()
    return {"unread": count}

@router.patch("/{nid}/read")
def mark_read(
    nid: int,
    data: NotificationReadIn,
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    if me["role"] != "visitor":
        raise HTTPException(403, "Only visitor can mark read")

    n = db.get(Notification, nid)
    if not n or n.visitor_id != int(me["sub"]):
        raise HTTPException(404, "Notification not found")

    n.is_read = 1 if data.is_read else 0
    db.commit()
    return {"ok": True, "id": n.id, "is_read": n.is_read}

@router.post("/read_all")
def mark_all_read(
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    if me["role"] != "visitor":
        raise HTTPException(403, "Only visitor can mark read")
    db.query(Notification).filter(
        Notification.visitor_id == int(me["sub"]),
        Notification.is_read == 0
    ).update({"is_read": 1})
    db.commit()
    return {"ok": True}
