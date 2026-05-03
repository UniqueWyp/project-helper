from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db, Project
from app.schemas import ProjectCreate, ProjectResponse
from app.tools.git_clone import extract_repo_name, remove_directory
import os

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    existing = db.query(Project).filter(Project.repo_url == project.repo_url).first()
    if existing:
        return existing
    
    project_name = extract_repo_name(project.repo_url)
    
    new_project = Project(
        repo_url=project.repo_url,
        name=project_name,
        status="pending",
        progress=0
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project

@router.get("/", response_model=list[ProjectResponse])
async def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.clone_path and os.path.exists(project.clone_path):
        remove_directory(project.clone_path)
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}
