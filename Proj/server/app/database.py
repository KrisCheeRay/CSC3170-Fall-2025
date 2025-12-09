import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

APP_DIR = os.path.dirname(os.path.abspath(__file__))      
SERVER_DIR = os.path.dirname(APP_DIR)                     
PROJECT_ROOT = os.path.dirname(SERVER_DIR)                
DB_PATH = os.path.join(PROJECT_ROOT, "vms.db")            
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
