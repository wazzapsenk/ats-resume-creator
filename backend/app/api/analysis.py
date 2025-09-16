from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.user import User
from ..models.analysis import Analysis, AnalysisStatus
from ..models.resume import Resume
from ..models.job_posting import JobPosting
from ..schemas.analysis import AnalysisCreate, AnalysisResponse
from .auth import get_current_user

router = APIRouter()

def get_analysis_by_id(db: Session, analysis_id: int, user_id: int):
    """Get analysis by ID and ensure it belongs to the user"""
    return db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

async def process_analysis_task(analysis_id: int, db: Session):
    """Background task to process analysis using analysis service"""
    from ..services.analysis import analysis_service

    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if analysis:
        # Get related resume and job posting
        resume = db.query(Resume).filter(Resume.id == analysis.resume_id).first()
        job_posting = db.query(JobPosting).filter(JobPosting.id == analysis.job_posting_id).first()

        if resume and job_posting:
            # Process the analysis
            analysis_service.analyze_resume_job_match(resume, job_posting, analysis, db)

@router.post("/", response_model=AnalysisResponse)
def create_analysis(
    analysis: AnalysisCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new resume-job analysis"""

    # Verify resume belongs to user
    resume = db.query(Resume).filter(
        Resume.id == analysis.resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Verify job posting belongs to user
    job_posting = db.query(JobPosting).filter(
        JobPosting.id == analysis.job_posting_id,
        JobPosting.user_id == current_user.id
    ).first()
    if not job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )

    # Create analysis record
    db_analysis = Analysis(
        user_id=current_user.id,
        resume_id=analysis.resume_id,
        job_posting_id=analysis.job_posting_id,
        status=AnalysisStatus.PENDING
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    # Add background task to process analysis
    background_tasks.add_task(process_analysis_task, db_analysis.id, db)

    return db_analysis

@router.get("/", response_model=List[AnalysisResponse])
def get_analyses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all analyses for the current user"""
    analyses = db.query(Analysis).filter(
        Analysis.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return analyses

@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific analysis"""
    analysis = get_analysis_by_id(db, analysis_id, current_user.id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    return analysis

@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an analysis"""
    analysis = get_analysis_by_id(db, analysis_id, current_user.id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    db.delete(analysis)
    db.commit()
    return {"message": "Analysis deleted successfully"}