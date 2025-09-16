from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.user import User
from ..models.resume import Resume
from ..schemas.resume import ResumeCreate, ResumeUpdate, ResumeResponse
from .auth import get_current_user

router = APIRouter()

def get_resume_by_id(db: Session, resume_id: int, user_id: int):
    """Get resume by ID and ensure it belongs to the user"""
    return db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == user_id
    ).first()

@router.post("/", response_model=ResumeResponse)
def create_resume(
    resume: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new resume"""
    db_resume = Resume(
        user_id=current_user.id,
        title=resume.title,
        full_name=resume.full_name,
        email=resume.email,
        phone=resume.phone,
        location=resume.location,
        linkedin_url=resume.linkedin_url,
        website_url=resume.website_url,
        summary=resume.summary,
        work_experience=resume.work_experience,
        education=resume.education,
        skills=resume.skills,
        certifications=resume.certifications,
        projects=resume.projects,
        languages=resume.languages
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

@router.get("/", response_model=List[ResumeResponse])
def get_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all resumes for the current user"""
    resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return resumes

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific resume"""
    resume = get_resume_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    return resume

@router.put("/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: int,
    resume_update: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a resume"""
    resume = get_resume_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Update fields that are provided
    update_data = resume_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resume, field, value)

    db.commit()
    db.refresh(resume)
    return resume

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a resume"""
    resume = get_resume_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}