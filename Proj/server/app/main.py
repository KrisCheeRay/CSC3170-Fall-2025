from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .auth import router as auth_router
from .reservations import router as reservation_router
from .locations import router as locations_router
from .notifications import router as notifications_router  

app = FastAPI(title="VMS API", version="0.1.0")

app.include_router(auth_router,          prefix="/auth",          tags=["auth"])
app.include_router(reservation_router,   prefix="/reservations",  tags=["reservations"])
app.include_router(locations_router,     prefix="/locations",     tags=["locations"])
app.include_router(notifications_router, prefix="/notifications", tags=["notifications"])  


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"ok": True}
