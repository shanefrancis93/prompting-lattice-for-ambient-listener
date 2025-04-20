import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///clips.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Clip(Base):
    __tablename__ = "clips"
    clip_id = Column(String, primary_key=True, index=True)
    device_id = Column(String)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    duration_ms = Column(Integer)
    bytes = Column(Integer)
    status = Column(String, default="pending")

# Create tables if they don't exist
def init_db():
    Base.metadata.create_all(bind=engine)
