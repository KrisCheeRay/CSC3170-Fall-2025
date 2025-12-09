from sqlalchemy.orm import Session
from .database import SessionLocal
from fastapi import Depends, Header, HTTPException,Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from .settings import JWT_SECRET, JWT_ALGO
security = HTTPBearer(auto_error=False)
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing token")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload