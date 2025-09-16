from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.user import User
from ..models.job_posting import JobPosting
from ..schemas.job_posting import JobPostingCreate, JobPostingUpdate, JobPostingResponse
from .auth import get_current_user

router = APIRouter()

def get_job_posting_by_id(db: Session, job_posting_id: int, user_id: int):
    """Get job posting by ID and ensure it belongs to the user"""
    return db.query(JobPosting).filter(
        JobPosting.id == job_posting_id,
        JobPosting.user_id == user_id
    ).first()

@router.post("/", response_model=JobPostingResponse)
def create_job_posting(
    job_posting: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new job posting"""
    db_job_posting = JobPosting(
        user_id=current_user.id,
        title=job_posting.title,
        company=job_posting.company,
        location=job_posting.location,
        job_type=job_posting.job_type,
        seniority_level=job_posting.seniority_level,
        description=job_posting.description,
        requirements=job_posting.requirements,
        responsibilities=job_posting.responsibilities,
        benefits=job_posting.benefits,
        source_url=job_posting.source_url,
        source_platform=job_posting.source_platform
    )
    db.add(db_job_posting)
    db.commit()
    db.refresh(db_job_posting)
    return db_job_posting

@router.get("/", response_model=List[JobPostingResponse])
def get_job_postings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all job postings for the current user"""
    job_postings = db.query(JobPosting).filter(
        JobPosting.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return job_postings

@router.get("/{job_posting_id}", response_model=JobPostingResponse)
def get_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific job posting"""
    job_posting = get_job_posting_by_id(db, job_posting_id, current_user.id)
    if not job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    return job_posting

@router.put("/{job_posting_id}", response_model=JobPostingResponse)
def update_job_posting(
    job_posting_id: int,
    job_posting_update: JobPostingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a job posting"""
    job_posting = get_job_posting_by_id(db, job_posting_id, current_user.id)
    if not job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )

    # Update fields that are provided
    update_data = job_posting_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job_posting, field, value)

    db.commit()
    db.refresh(job_posting)
    return job_posting

@router.delete("/{job_posting_id}")
def delete_job_posting(
    job_posting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a job posting"""
    job_posting = get_job_posting_by_id(db, job_posting_id, current_user.id)
    if not job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )

    db.delete(job_posting)
    db.commit()
    return {"message": "Job posting deleted successfully"}