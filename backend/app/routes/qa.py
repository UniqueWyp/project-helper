from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio
from app.database import get_db, Project
from app.services.analysis_service import AnalysisService
from app.schemas import QARequest

router = APIRouter()

analysis_service = AnalysisService()

@router.post("/")
async def ask_question(request: QARequest, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != "completed":
        raise HTTPException(status_code=400, detail="Project not analyzed yet")
    
    if not project.clone_path:
        raise HTTPException(status_code=400, detail="Project path not found")
    
    answer = analysis_service.answer_question(project.clone_path, request.question)
    
    return {
        "project_id": request.project_id,
        "question": request.question,
        "answer": answer
    }

@router.post("/stream")
async def ask_question_stream(request: QARequest, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != "completed":
        raise HTTPException(status_code=400, detail="Project not analyzed yet")
    
    if not project.clone_path:
        raise HTTPException(status_code=400, detail="Project path not found")
    
    async def event_stream():
        answer = analysis_service.answer_question(project.clone_path, request.question)
        
        for chunk in answer.split('\n'):
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.1)
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.get("/file/{project_id}")
async def get_file_content(project_id: int, file_path: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.clone_path:
        raise HTTPException(status_code=400, detail="Project path not found")
    
    full_path = f"{project.clone_path}/{file_path}"
    content = analysis_service.get_file_content(full_path)
    
    return {"file_path": file_path, "content": content}

@router.get("/search/{project_id}")
async def search_code(project_id: int, query: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.clone_path:
        raise HTTPException(status_code=400, detail="Project path not found")
    
    results = analysis_service.search_code(project.clone_path, query)
    
    return {"results": results}
