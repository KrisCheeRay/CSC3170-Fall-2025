from __future__ import annotations
from typing import Optional
from datetime import datetime
from enum import Enum as PyEnum
import re
from typing import Annotated
from pydantic import BaseModel, Field, EmailStr, constr



PhoneStr = Annotated[str, Field(pattern=r"^\d{11}$", description="11-digit phone number")]



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    pending_reservations: int


class VisitorRegisterIn(BaseModel):
    name: str
    phone: PhoneStr
    org: str | None = None
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class VisitorLoginIn(BaseModel):
    identifier: str = Field(..., description="Email or Phone Number")
    password: str

    @staticmethod
    def _is_email(s: str) -> bool:
        return "@" in s and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s) is not None

    @staticmethod
    def _is_phone(s: str) -> bool:
        return re.match(r"^\d{11}$", s) is not None

    def normalized(self) -> tuple[str, str]:
        raw = self.identifier.strip()
        if self._is_email(raw):
            return ("email", raw.lower())
        if self._is_phone(raw):
            return ("phone", raw)
        raise ValueError("identifier must be a valid email or phone number")


class VisitorResetPasswordIn(BaseModel):
    email: EmailStr
    phone: PhoneStr
    new_password: str = Field(min_length=6, max_length=72)


class AdminLoginIn(BaseModel):
    username: str
    password: str


class CampusEnum(str, PyEnum):
    LOWER = "LOWER"
    MIDDLE = "MIDDLE"
    UPPER = "UPPER"



class ReservationCreateIn(BaseModel):
    campus: CampusEnum
    start_time: datetime = Field(..., description="ISO8601, for example 2025-11-20T09:30:00")
    end_time: datetime
    location_id: int
    purpose: str | None = None

    is_driving: bool = Field(default=False, description="Driving or not")
    plate_number: str | None = Field(
        default=None,
        pattern=r"^[A-Z0-9]{6}$",
        description="6-character license plate number (letters and numbers)"
    )

    @classmethod
    def validate_driving(cls, values):
        is_driving = values.get("is_driving", False)
        plate_number = values.get("plate_number")
        if is_driving and not plate_number:
            raise ValueError("When driving, the license plate number must be filled in")
        if not is_driving and plate_number:
            raise ValueError("When not driving, the license plate number should not be filled in")
        return values

    model_config = {
        "validate_assignment": True
    }


class ReservationOut(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    location: str
    purpose: str | None = None
    status: str
    visitor_id: int
    is_driving: bool
    plate_number: str | None = None

    class Config:
        from_attributes = True

class NotificationOut(BaseModel):
    id: int
    type: str
    reservation_id: int | None = None
    title: str
    body: str | None = None
    is_read: int
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationReadIn(BaseModel):
    is_read: bool = True

class VisitorUpdateIn(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: PhoneStr | None = None
    org: str | None = None
    new_password: str | None = Field(None, min_length=6, max_length=72)

class AdminProfileOut(BaseModel):
    username: str
    email: EmailStr | None = None
    phone: PhoneStr | None = None
    org: str | None = None
    work_address: str | None = None
    display_name: str | None = None

class AdminProfileIn(BaseModel):
    email: EmailStr | None = None
    phone: PhoneStr | None = None
    org: str | None = None
    work_address: str | None = None
    display_name: str | None = None

class AdminCreateIn(BaseModel):
    username: str
    password: str

class LocationCreateIn(BaseModel):
    campus: CampusEnum
    name: str

class LocationUpdateIn(BaseModel):
    campus: Optional[CampusEnum] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None

class LocationAdminOut(BaseModel):
    id: int
    campus: str
    name: str
    is_active: int

    class Config:
        from_attributes = True