from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .deps import get_db, get_current
from .models import Location
from .schemas import CampusEnum,LocationCreateIn, LocationUpdateIn, LocationAdminOut
from sqlalchemy import and_
router = APIRouter()

@router.get("/", summary="Filtered locations grouped by campus")
def list_locations(db: Session = Depends(get_db)):
    rows = db.query(Location).filter(Location.is_active == 1).order_by(Location.campus, Location.name).all()
    grouped = {"LOWER": [], "MIDDLE": [], "UPPER": []}
    for r in rows:
        grouped.setdefault(r.campus, []).append({"id": r.id, "name": r.name})
    return grouped

@router.get("/flat", summary="Flat list of active locations")
def list_locations_flat(db: Session = Depends(get_db)):
    rows = db.query(Location).filter(Location.is_active == 1).order_by(Location.campus, Location.name).all()
    return [{"id": r.id, "campus": r.campus, "name": r.name} for r in rows]


@router.get("/campus", response_model=list[str])
def list_campus():
    return [c.value for c in CampusEnum]

def _ensure_superadmin(me):
    if me["role"] != "superadmin":
        raise HTTPException(403, "Only superadmin can manage locations")

@router.get("/admin/all", response_model=list[LocationAdminOut], summary="List all locations (superadmin only)")
def admin_list_all_locations(
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    _ensure_superadmin(me)
    rows = db.query(Location).order_by(Location.campus, Location.name).all()
    return rows

@router.post("/admin", response_model=LocationAdminOut, summary="(superadmin) Create a new location")
def admin_create_location(
    data: LocationCreateIn,
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    _ensure_superadmin(me)
    campus = data.campus.value if hasattr(data.campus, "value") else str(data.campus)
    name = data.name.strip()
    if not name:
        raise HTTPException(422, "name must not be empty")

    exists = db.query(Location).filter(
        and_(Location.campus == campus, Location.name == name)
    ).first()
    if exists:
        raise HTTPException(400, "A location with the same name already exists in this campus")

    loc = Location(campus=campus, name=name, is_active=1)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc

@router.put("/admin/{loc_id}", response_model=LocationAdminOut, summary="(superadmin) Update a location")
def admin_update_location(
    loc_id: int,
    data: LocationUpdateIn,
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    _ensure_superadmin(me)

    loc = db.get(Location, loc_id)
    if not loc:
        raise HTTPException(404, "Location not found")

    if data.campus is not None:
        loc.campus = data.campus.value if hasattr(data.campus, "value") else str(data.campus)
    if data.name is not None:
        new_name = data.name.strip()
        if not new_name:
            raise HTTPException(422, "name 不能为空")
        loc.name = new_name
    if data.is_active is not None:
        loc.is_active = 1 if data.is_active else 0

    dup = db.query(Location).filter(
        and_(Location.campus == loc.campus, Location.name == loc.name, Location.id != loc.id)
    ).first()
    if dup:
        raise HTTPException(400, "A location with the same name already exists in this campus")

    db.commit()
    db.refresh(loc)
    return loc

@router.patch("/admin/{loc_id}/active", summary="(superadmin) Enable/Disable location")
def admin_toggle_location(
    loc_id: int,
    is_active: bool = Query(..., description="true=Enable, false=Disable"),
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    _ensure_superadmin(me)
    loc = db.get(Location, loc_id)
    if not loc:
        raise HTTPException(404, "Location not found")

    loc.is_active = 1 if is_active else 0
    db.commit()
    return {"ok": True, "id": loc.id, "is_active": loc.is_active}

@router.delete("/admin/{loc_id}", summary="(superadmin) Delete a location")
def admin_delete_location(
    loc_id: int,
    db: Session = Depends(get_db),
    me = Depends(get_current),
):
    _ensure_superadmin(me)
    loc = db.get(Location, loc_id)
    if not loc:
        raise HTTPException(404, "Location not found")
    db.delete(loc)
    db.commit()
    return {"ok": True}