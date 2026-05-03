from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import logging
from app.database import get_db, Project, AnalysisProgress, SessionLocal
from app.services.analysis_service import AnalysisService

router = APIRouter()

analysis_service = AnalysisService()

logger = logging.getLogger(__name__)

@router.post("/{project_id}")
async def start_analysis(project_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status == "analyzing":
        raise HTTPException(status_code=400, detail="Analysis already in progress")
    
    project.status = "analyzing"
    project.progress = 0
    db.commit()
    
    def analyze_task():
        task_db = SessionLocal()
        try:
            logger.info(f"Starting analysis for project {project_id}")
            
            # 在后台任务中重新获取项目对象
            project_obj = task_db.query(Project).filter(Project.id == project_id).first()
            if not project_obj:
                logger.error(f"Project {project_id} not found")
                raise Exception("Project not found")
            
            logger.info(f"Project URL: {project_obj.repo_url}")
            
            def progress_callback(step: str, message: str, progress: int):
                logger.info(f"Progress update - Step: {step}, Message: {message}, Progress: {progress}%")
                proj = task_db.query(Project).filter(Project.id == project_id).first()
                if proj:
                    proj.status = "analyzing"
                    proj.progress = progress
                    proj.updated_at = datetime.now()
                    task_db.commit()
                
                progress_record = AnalysisProgress(
                    project_id=project_id,
                    step=step,
                    message=message
                )
                task_db.add(progress_record)
                task_db.commit()
            
            progress_callback("init", "初始化分析任务...", 5)
            
            result = analysis_service.analyze_project(
                repo_url=project_obj.repo_url,
                progress_callback=progress_callback
            )
            
            project_obj = task_db.query(Project).filter(Project.id == project_id).first()
            if project_obj:
                project_obj.report = result['report']
                project_obj.clone_path = result['clone_path']
                project_obj.status = "completed"
                project_obj.progress = 100
                project_obj.last_analyzed_at = datetime.now()
                project_obj.updated_at = datetime.now()
                task_db.commit()
            
            logger.info(f"Analysis completed for project {project_id}")
        except Exception as e:
            logger.error(f"Analysis failed for project {project_id}: {str(e)}")
            project_obj = task_db.query(Project).filter(Project.id == project_id).first()
            if project_obj:
                project_obj.status = "failed"
                project_obj.updated_at = datetime.now()
                task_db.commit()
            
            progress_record = AnalysisProgress(
                project_id=project_id,
                step="error",
                message=str(e)
            )
            task_db.add(progress_record)
            task_db.commit()
        finally:
            task_db.close()
    
    background_tasks.add_task(analyze_task)
    
    return {"message": "Analysis started", "project_id": project_id}

@router.get("/{project_id}/progress")
async def get_analysis_progress(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    progress = db.query(AnalysisProgress)\
        .filter(AnalysisProgress.project_id == project_id)\
        .order_by(AnalysisProgress.timestamp.desc())\
        .first()
    
    return {
        "project_id": project.id,
        "status": project.status,
        "progress": project.progress,
        "last_message": progress.message if progress else ""
    }

@router.get("/{project_id}/report")
async def get_analysis_report(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    return {
        "project_id": project.id,
        "report": project.report,
        "generated_at": project.last_analyzed_at
    }

@router.post("/{project_id}/cancel")
async def cancel_analysis(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != "analyzing":
        raise HTTPException(status_code=400, detail="Analysis is not in progress")
    
    project.status = "cancelled"
    project.updated_at = datetime.now()
    db.commit()
    
    progress_record = AnalysisProgress(
        project_id=project_id,
        step="cancel",
        message="分析已取消"
    )
    db.add(progress_record)
    db.commit()
    
    return {"message": "Analysis cancelled", "project_id": project_id}

@router.get("/{project_id}/progress/stream")
async def stream_analysis_progress(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    async def event_stream():
        last_progress_id = 0
        
        while True:
            progress = db.query(AnalysisProgress)\
                .filter(AnalysisProgress.project_id == project_id)\
                .order_by(AnalysisProgress.id.desc())\
                .first()
            
            if progress and progress.id > last_progress_id:
                last_progress_id = progress.id
                yield f"data: {progress.message}\n\n"
            
            project_obj = db.query(Project).filter(Project.id == project_id).first()
            if project_obj and project_obj.status in ["completed", "failed", "cancelled"]:
                yield f"data: {project_obj.status}\n\n"
                break
            
            await asyncio.sleep(1)
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
