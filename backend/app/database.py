from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./project_helper.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_url = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    clone_path = Column(String)
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)
    report = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    last_analyzed_at = Column(DateTime)

class AnalysisProgress(Base):
    __tablename__ = "analysis_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer)
    step = Column(String)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.now)

def init_db():
    os.makedirs(os.path.dirname(SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
