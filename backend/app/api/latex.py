from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.user import User
from ..models.resume import Resume
from .auth import get_current_user

router = APIRouter()

@router.post("/generate-pdf/{resume_id}")
async def generate_pdf(
    resume_id: int,
    template_name: str = "modern",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate PDF from resume data using LaTeX template"""

    # Get resume
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Placeholder for LaTeX service (to be implemented by LaTeX Developer)
    return {
        "message": "PDF generation service not yet implemented",
        "resume_id": resume_id,
        "template": template_name,
        "status": "pending"
    }

@router.get("/templates")
async def get_templates():
    """Get available LaTeX templates"""
    # Placeholder - will be implemented by LaTeX Developer
    return {
        "templates": [
            {
                "name": "modern",
                "description": "Modern clean design",
                "preview_url": None
            },
            {
                "name": "classic",
                "description": "Traditional professional format",
                "preview_url": None
            },
            {
                "name": "ats-optimized",
                "description": "ATS-friendly format",
                "preview_url": None
            }
        ]
    }