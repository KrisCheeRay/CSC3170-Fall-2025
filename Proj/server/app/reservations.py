from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, time, date, timedelta
from sqlalchemy import case, func,desc
from .deps import get_db, get_current
from .models import Reservation, Location, Notification, Visitor
from .schemas import ReservationCreateIn, ReservationOut

router = APIRouter()

BUSINESS_START = time(9, 0)   
BUSINESS_END   = time(17, 0)   

def normalize_minute(dt: datetime) -> datetime:
    return dt.replace(second=0, microsecond=0)

def assert_business_hours(start: datetime, end: datetime):
    if end <= start:
        raise HTTPException(400, "end_time must be greater than start_time")
    if start.date() != end.date():
        raise HTTPException(400, "start_time and end_time must be on the same day")

    st, et = start.time(), end.time()
    if not (BUSINESS_START <= st < BUSINESS_END):
        raise HTTPException(400, "start_time must be within 09:00–17:00 (inclusive 09:00, exclusive 17:00)")
    if not (BUSINESS_START < et <= BUSINESS_END):
        raise HTTPException(400, "end_time must be within 09:00–17:00 (exclusive 09:00, inclusive 17:00)")

def resolve_location_id(db: Session, location_id: int | None, campus: str) -> tuple[int, str]:
    if not location_id:
        raise HTTPException(400, "location_id is required")

    campus = (campus or "").upper()
    if campus not in {"LOWER", "MIDDLE", "UPPER"}:
        raise HTTPException(400, "Invalid campus. Must be LOWER/MIDDLE/UPPER")

    loc = db.get(Location, location_id)
    if not loc or loc.is_active != 1 or (loc.campus or "").upper() != campus:
        raise HTTPException(400, f"Invalid location_id for campus {campus}")
    return loc.id, loc.name



@router.post("/", response_model=ReservationOut, operation_id="reservations_create")
def create_reservation(
    data: ReservationCreateIn,
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    if me["role"] != "visitor":
        raise HTTPException(403, "Only visitor can create")


    start = normalize_minute(data.start_time)
    end   = normalize_minute(data.end_time)

    assert_business_hours(start, end)

    campus_val = data.campus.value if hasattr(data.campus, "value") else data.campus
    loc_id, loc_name = resolve_location_id(db, data.location_id, campus_val)

    r = Reservation(
    visitor_id=int(me["sub"]),
    start_time=start,
    end_time=end,
    location=loc_name,
    location_id=loc_id,
    purpose=data.purpose,
    status="pending",
    is_driving=1 if data.is_driving else 0,
    plate_number=data.plate_number if data.is_driving else None
    )

    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.get("/", response_model=list[ReservationOut])
def list_my_reservations(
    status: str | None = Query(None, pattern="^(pending|approved|denied)$"),
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    if me["role"] != "visitor":
        raise HTTPException(403, "Only visitor can list their reservations")
    q = db.query(Reservation).filter(Reservation.visitor_id == int(me["sub"]))
    if status:
        q = q.filter(Reservation.status == status)
    return q.order_by(Reservation.start_time.desc()).all()

@router.put("/{resv_id}", response_model=ReservationOut, operation_id="reservations_update")
def update_reservation(
    resv_id: int,
    data: ReservationCreateIn,  
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    if me["role"] != "visitor":
        raise HTTPException(403, "Only visitor can update")

    r = db.get(Reservation, resv_id)
    if not r or r.visitor_id != int(me["sub"]):
        raise HTTPException(404, "Reservation not found")
    if r.status != "pending":
        raise HTTPException(400, "Only pending reservation can be updated")

    start = normalize_minute(data.start_time)
    end   = normalize_minute(data.end_time)

    assert_business_hours(start, end)

    campus_val = data.campus.value if hasattr(data.campus, "value") else data.campus
    loc_id, loc_name = resolve_location_id(db, data.location_id, campus_val)

    r.start_time  = start
    r.end_time    = end
    r.location    = loc_name     
    r.location_id = loc_id       
    r.purpose     = data.purpose
    r.updated_at  = datetime.utcnow()
    r.is_driving  = 1 if data.is_driving else 0
    r.plate_number = data.plate_number if data.is_driving else None
    db.commit()
    db.refresh(r)
    return r

@router.delete("/{resv_id}")
def delete_reservation(
    resv_id: int,
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    if me["role"] != "visitor":
        raise HTTPException(403, "Only visitor can delete")
    r = db.get(Reservation, resv_id)
    if not r or r.visitor_id != int(me["sub"]):
        raise HTTPException(404, "Reservation not found")
    if r.status != "pending":
        raise HTTPException(400, "Only pending reservation can be deleted")

    db.delete(r)
    db.commit()
    return {"ok": True}


@router.put("/{resv_id}/decision")
def decision(
    resv_id: int,
    decision: str = Query(..., pattern="^(approved|denied)$"),
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    if me["role"] != "admin":
        raise HTTPException(403, "Only admin can approve/deny")

    r = db.get(Reservation, resv_id)
    if not r:
        raise HTTPException(404, "Reservation not found")
    if r.status not in ("pending",):
        raise HTTPException(400, "Only pending reservation can be decided")


    r.status = decision
    r.updated_at = datetime.utcnow()

    title = "Reservation Approval Result"
    body = f"Your reservation on {r.start_time:%Y-%m-%d %H:%M} at {r.location} has been {decision.upper()}."
    db.add(Notification(
        visitor_id=r.visitor_id,
        type="reservation_status",
        reservation_id=r.id,
        title=title,
        body=body,
        is_read=0,
    ))

    db.commit()
    return {"ok": True, "status": r.status}
@router.get("/admin/reservations", summary="Admin view all reservations")
def admin_list_reservations(
    location_id: int | None = Query(None, description="Filter by location"),
    date: str | None = Query(None, description="Filter by date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    me=Depends(get_current)
):
    if me["role"] != "admin":
        raise HTTPException(403, "Only admin can view all reservations")

    query = db.query(Reservation).join(Visitor).join(Location)

    if location_id is not None:
        query = query.filter(Reservation.location_id == location_id)

    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(422, "Invalid date format. Must be YYYY-MM-DD")
        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = datetime.combine(target_date, datetime.max.time())
        query = query.filter(
            Reservation.start_time >= start_dt,
            Reservation.start_time <= end_dt
        )

    results = query.order_by(Reservation.start_time.desc()).all()

    output = []
    for r in results:
        output.append({
            "id": r.id,
            "visitor_name": r.visitor.name,
            "visitor_org": r.visitor.org,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "campus": r.location_obj.campus if r.location_obj else None,
            "location": r.location_obj.name if r.location_obj else None,
            "purpose": r.purpose,
            "status": r.status,
            "is_driving": bool(r.is_driving),
            "plate_number": r.plate_number,
        })

    return {
        "count": len(output),
        "results": output
    }

@router.get("/admin/report/daily", summary="Admin daily reservation report")
def daily_report(date: str = None, db: Session = Depends(get_db), me=Depends(get_current)):
    if me["role"] != "admin":
        raise HTTPException(403, "Only admin can view daily reports")

    if date:
        try:
            report_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(422, "Invalid date format. Must be YYYY-MM-DD")
    else:
        report_date = datetime.today().date()

    day_start = report_date
    day_end   = report_date + timedelta(days=1)  

    all_count = func.count(Reservation.id).label("reservation_count")
    approved_sum = func.sum(
        case((Reservation.status == "approved", 1), else_=0)
    ).label("approved_count")

    most_booked = (
        db.query(
            Reservation.location_id,
            Location.name.label("location_name"),
            all_count,      
            approved_sum,   
        )
        .join(Location, Reservation.location_id == Location.id)
        .filter(Reservation.start_time >= day_start, Reservation.start_time < day_end)
        .group_by(Reservation.location_id, Location.name)
        .order_by(all_count.desc(), approved_sum.desc())   
        .first()
    )


    
    approved_sum = func.sum(
        case((Reservation.status == "approved", 1), else_=0)
    ).label("approved_count")
    all_count = func.count(Reservation.id).label("reservation_count")

    most_visited = (
        db.query(
            Reservation.location_id,
            Location.name.label("location_name"),
            approved_sum,  
            all_count,      
        )
        .join(Location, Reservation.location_id == Location.id)
        .filter(Reservation.start_time >= day_start, Reservation.start_time < day_end)
        .group_by(Reservation.location_id, Location.name)
        .order_by(approved_sum.desc(), all_count.desc())   
        .first()
    )

    reservation_status_count = (
        db.query(
            func.count(Reservation.id).label("total_reservations"),
            func.sum(case((Reservation.status == "pending", 1), else_=0)).label("pending_count"),
            func.sum(case((Reservation.status == "approved", 1), else_=0)).label("approved_count"),
            func.sum(case((Reservation.status == "denied", 1), else_=0)).label("denied_count"),
        )
        .filter(Reservation.start_time >= day_start, Reservation.start_time < day_end)
        .first()
    )

    day_expr = func.date(Reservation.start_time)  
    uv_days_subq = (
        db.query(
            Reservation.visitor_id.label("vid"),
            day_expr.label("d"),
        )
        .filter(
            Reservation.start_time < day_end,     
            Reservation.status == "approved",
        )
        .group_by(Reservation.visitor_id, day_expr)
        .subquery()
    )
    total_unique_visitor_days_up_to_date = (
        db.query(func.count()).select_from(uv_days_subq).scalar() or 0
    )

    return {
        "most_booked_location": {
            "location_name": most_booked.location_name if most_booked else "No data",
            "reservation_count": int(most_booked.reservation_count) if most_booked else 0,  
            "approved_count": int(most_booked.approved_count) if most_booked else 0,
        },
        "most_visited_location": {
            "location_name": most_visited.location_name if most_visited else "No data",
            "approved_count": int(most_visited.approved_count) if most_visited else 0,      
            "reservation_count": int(most_visited.reservation_count) if most_visited else 0 
        },
        "daily_stats": {
            "total_reservations": int(reservation_status_count.total_reservations) if reservation_status_count else 0,
            "pending_count": int(reservation_status_count.pending_count) if reservation_status_count else 0,
            "approved_count": int(reservation_status_count.approved_count) if reservation_status_count else 0,
            "denied_count": int(reservation_status_count.denied_count) if reservation_status_count else 0,
            "total_unique_visitor_days_up_to_date": int(total_unique_visitor_days_up_to_date),
        },
        "as_of": str(report_date),
    }



