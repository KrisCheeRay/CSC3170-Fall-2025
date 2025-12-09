from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from .deps import get_db, get_current
from .models import Visitor, Admin, Reservation
from .schemas import VisitorRegisterIn, VisitorLoginIn, Token, AdminLoginIn,VisitorResetPasswordIn, VisitorUpdateIn, AdminProfileIn, AdminProfileOut,AdminCreateIn
from .settings import JWT_SECRET, JWT_ALGO, JWT_EXPIRES_MIN
from passlib.hash import pbkdf2_sha256 as hasher 
import re

router = APIRouter()

def create_token(sub: str, role: str) -> str:
    payload = {"sub": sub, "role": role,
               "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_MIN)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

@router.post("/visitor/register")
def visitor_register(data: VisitorRegisterIn, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    phone = data.phone.strip()  

    if db.query(Visitor).filter(Visitor.phone == phone).first():
        raise HTTPException(400, "Phone already exists")
    if db.query(Visitor).filter(Visitor.email == email).first():
        raise HTTPException(400, "Email already exists")

    v = Visitor(
        name=data.name.strip(),
        phone=phone,
        org=(data.org or "").strip() or None,
        email=email,
        password_hash=hasher.hash(data.password),
    )
    db.add(v); db.commit(); db.refresh(v)
    return {"access_token": create_token(str(v.id), "visitor")}

@router.post("/visitor/login")
def visitor_login(data: VisitorLoginIn, db: Session = Depends(get_db)):
    try:
        kind, value = data.normalized()
    except ValueError as e:
        raise HTTPException(422, str(e))

    if kind == "email":
        v = db.query(Visitor).filter(Visitor.email == value).first()
    else:
        v = db.query(Visitor).filter(Visitor.phone == value).first()

    if not v or not hasher.verify(data.password, v.password_hash):
        raise HTTPException(401, "Invalid credentials")

    return {"access_token": create_token(str(v.id), "visitor")}

@router.get("/me")
def me(db: Session = Depends(get_db), me=Depends(get_current)):
    if me["role"] == "visitor":
        v = db.get(Visitor, int(me["sub"]))
        if not v:
            raise HTTPException(404, "Visitor not found")
        return {"id": v.id, "name": v.name, "phone": v.phone, "org": v.org, "email": v.email}
    return {"role": me["role"], "sub": me["sub"]}


@router.post("/admin/login")
def admin_login(data: AdminLoginIn, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == data.username).first()
    if not admin or not hasher.verify(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    role = admin.role or "admin"
    if admin.username.strip().lower() == "root":
        role = "superadmin"
    pending_count = db.query(Reservation).filter(Reservation.status == "pending").count()
    token = create_token(admin.username, admin.role)

    need_profile = not (admin.email and admin.phone and admin.org and admin.work_address)

    return {
        "access_token": token,
        "token_type": "bearer",
        "need_profile": need_profile,
        "pending_reservations": pending_count,
        "role": admin.role
    }

@router.post("/visitor/password/reset")
def visitor_reset_password(data: VisitorResetPasswordIn, db: Session = Depends(get_db)):
    v = db.query(Visitor).filter(
        Visitor.email == data.email,
        Visitor.phone == data.phone
    ).first()
    if not v:
        raise HTTPException(404, "Visitor not found by email+phone")

    v.password_hash = hasher.hash(data.new_password)
    db.commit()
    return {"ok": True}


@router.put("/visitor/profile")
def update_visitor_profile(
    data: VisitorUpdateIn,
    db: Session = Depends(get_db),
    me=Depends(get_current)
):
    if me["role"] != "visitor":
        raise HTTPException(403, "Only visitor can update profile")

    v = db.get(Visitor, int(me["sub"]))
    if not v:
        raise HTTPException(404, "Visitor not found")

    
    if data.name:
        v.name = data.name.strip() 


    if data.email:
        email = data.email.strip().lower()
        if db.query(Visitor).filter(Visitor.email == email, Visitor.id != v.id).first():
            raise HTTPException(400, "Email already used")
        v.email = email

    if data.phone:
        phone = data.phone.strip()
        if db.query(Visitor).filter(Visitor.phone == phone, Visitor.id != v.id).first():
            raise HTTPException(400, "Phone already used")
        v.phone = phone

    if data.org is not None:
        v.org = data.org.strip() or None  

    if data.new_password:
        v.password_hash = hasher.hash(data.new_password)

    db.commit()
    db.refresh(v)

    return {
        "ok": True,
        "updated": {
            "name": v.name,
            "email": v.email,
            "phone": v.phone,
            "org": v.org,
        }
    }
@router.get("/admin/profile", response_model=AdminProfileOut)
def admin_profile(me=Depends(get_current), db: Session = Depends(get_db)):
    if me["role"] not in ("admin", "superadmin"):
        raise HTTPException(403, "Only admin can view profile")
    admin = db.query(Admin).filter(Admin.username == me["sub"]).first()
    if not admin:
        raise HTTPException(404, "Admin not found")
    return admin

@router.put("/admin/profile", response_model=AdminProfileOut)
def admin_profile_update(
    data: AdminProfileIn,
    me=Depends(get_current),
    db: Session = Depends(get_db)
):
    if me["role"] not in ("admin", "superadmin"):
        raise HTTPException(403, "Only admin can update profile")
    admin = db.query(Admin).filter(Admin.username == me["sub"]).first()
    if not admin:
        raise HTTPException(404, "Admin not found")

    if data.email:
        email = data.email.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            raise HTTPException(422, "The email format is invalid")
        if db.query(Admin).filter(Admin.email == email, Admin.id != admin.id).first():
            raise HTTPException(400, "Email already used")
        admin.email = email

    if data.phone:
        phone = data.phone.strip()
        if not re.match(r"^\d{11}$", phone):
            raise HTTPException(422, "The phone format is invalid")
        if db.query(Admin).filter(Admin.phone == phone, Admin.id != admin.id).first():
            raise HTTPException(400, "Phone already used")
        admin.phone = phone

    if data.org is not None:
        admin.org = data.org.strip() or None
    if data.work_address is not None:
        admin.work_address = data.work_address.strip() or None
    if data.display_name is not None:
        admin.display_name = data.display_name.strip() or None

    db.commit()
    db.refresh(admin)
    return admin

@router.post("/superadmin/admins", summary="Create a normal admin (superadmin only)")
def superadmin_create_admin(
    data: AdminCreateIn,
    db: Session = Depends(get_db),
    me = Depends(get_current)
):
    if me["role"] != "superadmin":
        raise HTTPException(403, "Only superadmin can create admins")

    username = data.username.strip()
    if db.query(Admin).filter(Admin.username == username).first():
        raise HTTPException(400, "Username already exists")

    admin = Admin(
        username=username,
        password_hash=hasher.hash(data.password),
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return {"ok": True, "id": admin.id, "username": admin.username, "role": admin.role}

@router.get("/visitor/profile")
def get_visitor_profile(db: Session = Depends(get_db), me=Depends(get_current)):
    if me["role"] != "visitor":
        raise HTTPException(403, "Only visitor can view profile")
    v = db.get(Visitor, int(me["sub"]))
    if not v:
        raise HTTPException(404, "Visitor not found")
    return {
        "id": v.id,
        "name": v.name,
        "phone": v.phone,
        "org": v.org,
        "email": v.email,
    }
