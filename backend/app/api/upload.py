from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.user import User
from ..services.file_upload import file_upload_service
from .auth import get_current_user

router = APIRouter()

@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a resume file"""
    try:
        file_path = file_upload_service.save_resume_file(file, current_user.id)
        file_info = file_upload_service.get_file_info(file_path)

        return {
            "message": "Resume uploaded successfully",
            "file_path": file_path,
            "file_info": file_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.post("/job-posting")
async def upload_job_posting(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a job posting file"""
    try:
        file_path = file_upload_service.save_job_posting_file(file, current_user.id)
        file_info = file_upload_service.get_file_info(file_path)

        return {
            "message": "Job posting uploaded successfully",
            "file_path": file_path,
            "file_info": file_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.delete("/file")
async def delete_file(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an uploaded file"""
    # Security check: ensure file path contains user ID
    if f"_{current_user.id}_" not in file_path:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this file"
        )

    success = file_upload_service.delete_file(file_path)
    if success:
        return {"message": "File deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or could not be deleted"
        )