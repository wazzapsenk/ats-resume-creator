from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from pathlib import Path

from ..database import get_db
from ..models.user import User
from ..models.resume import Resume
from ..auth import get_current_user
from ..services.latex_service import latex_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pdf", tags=["PDF Generation"])

@router.get("/templates")
async def get_available_templates():
    """Get list of available LaTeX templates"""
    try:
        templates = latex_service.get_available_templates()
        return {
            "success": True,
            "templates": templates
        }
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")

@router.get("/templates/{template_id}")
async def get_template_info(template_id: str):
    """Get detailed information about a specific template"""
    try:
        template_info = latex_service.get_template_info(template_id)

        if not template_info:
            raise HTTPException(status_code=404, detail="Template not found")

        return {
            "success": True,
            "template": template_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template info")

@router.get("/templates/{template_id}/preview")
async def get_template_preview(template_id: str):
    """Get template preview image"""
    try:
        preview_path = latex_service.preview_template(template_id)

        if not preview_path or not Path(preview_path).exists():
            raise HTTPException(status_code=404, detail="Preview image not found")

        return FileResponse(
            preview_path,
            media_type="image/png",
            filename=f"{template_id}_preview.png"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template preview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template preview")

@router.post("/generate/{resume_id}")
async def generate_resume_pdf(
    resume_id: int,
    template_id: str = "modern",
    filename: Optional[str] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate PDF from resume using specified template"""
    try:
        # Get resume
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        ).first()

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Validate LaTeX installation
        latex_valid, latex_message = latex_service.validate_latex_installation()
        if not latex_valid:
            raise HTTPException(status_code=500, detail=f"LaTeX not available: {latex_message}")

        # Prepare resume data
        resume_data = {
            "first_name": resume.first_name or "",
            "last_name": resume.last_name or "",
            "email": resume.email or "",
            "phone": resume.phone or "",
            "website": resume.website or "",
            "linkedin": resume.linkedin or "",
            "address": resume.address or "",
            "title": resume.title or "",
            "summary": resume.summary or "",
            "photo": resume.photo_url or "",
            "work_experience": resume.work_experience or [],
            "education": resume.education or [],
            "skills": resume.skills or [],
            "projects": resume.projects or [],
            "certifications": resume.certifications or [],
            "languages": resume.languages or [],
            "awards": resume.awards or []
        }

        # Generate PDF
        success, message, pdf_path = latex_service.generate_pdf(
            resume_data,
            template_id,
            filename or f"resume_{current_user.username}_{template_id}"
        )

        if not success:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {message}")

        if not pdf_path or not Path(pdf_path).exists():
            raise HTTPException(status_code=500, detail="PDF file not found after generation")

        # Return PDF file
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{Path(pdf_path).stem}.pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

@router.post("/generate/custom")
async def generate_custom_pdf(
    resume_data: dict,
    template_id: str = "modern",
    filename: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Generate PDF from custom resume data (not stored in database)"""
    try:
        # Validate LaTeX installation
        latex_valid, latex_message = latex_service.validate_latex_installation()
        if not latex_valid:
            raise HTTPException(status_code=500, detail=f"LaTeX not available: {latex_message}")

        # Generate PDF
        success, message, pdf_path = latex_service.generate_pdf(
            resume_data,
            template_id,
            filename or f"custom_resume_{current_user.username}_{template_id}"
        )

        if not success:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {message}")

        if not pdf_path or not Path(pdf_path).exists():
            raise HTTPException(status_code=500, detail="PDF file not found after generation")

        # Return PDF file
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{Path(pdf_path).stem}.pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

@router.get("/validate")
async def validate_latex_installation():
    """Validate LaTeX installation status"""
    try:
        is_valid, message = latex_service.validate_latex_installation()

        return {
            "success": True,
            "latex_available": is_valid,
            "message": message
        }
    except Exception as e:
        logger.error(f"LaTeX validation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate LaTeX installation")

@router.get("/status")
async def get_pdf_service_status():
    """Get PDF generation service status"""
    try:
        latex_valid, latex_message = latex_service.validate_latex_installation()
        templates = latex_service.get_available_templates()
        cache_stats = latex_service.get_cache_stats()

        return {
            "success": True,
            "status": {
                "latex_available": latex_valid,
                "latex_message": latex_message,
                "templates_count": len(templates),
                "available_templates": [t["id"] for t in templates],
                "cache_stats": cache_stats
            }
        }
    except Exception as e:
        logger.error(f"Failed to get PDF service status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service status")

@router.post("/cache/clear")
async def clear_pdf_cache(current_user: User = Depends(get_current_user)):
    """Clear PDF cache"""
    try:
        latex_service.clear_cache()
        return {
            "success": True,
            "message": "PDF cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

@router.get("/cache/stats")
async def get_cache_stats(current_user: User = Depends(get_current_user)):
    """Get PDF cache statistics"""
    try:
        stats = latex_service.get_cache_stats()
        return {
            "success": True,
            "cache_stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache statistics")