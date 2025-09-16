import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from ..core.config import settings

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}
MAX_FILE_SIZE = settings.MAX_FILE_SIZE  # 10MB

class FileUploadService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)

        # Create subdirectories
        (self.upload_dir / "cvs").mkdir(exist_ok=True)
        (self.upload_dir / "job-postings").mkdir(exist_ok=True)

    def validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        # Check file extension
        file_ext = Path(file.filename).suffix.lower() if file.filename else ""
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Check file size (if provided)
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
            )

    def save_resume_file(self, file: UploadFile, user_id: int) -> str:
        """Save uploaded resume file"""
        self.validate_file(file)

        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower() if file.filename else ".txt"
        filename = f"resume_{user_id}_{file.filename}"
        file_path = self.upload_dir / "cvs" / filename

        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not save file: {str(e)}"
            )

        return str(file_path)

    def save_job_posting_file(self, file: UploadFile, user_id: int) -> str:
        """Save uploaded job posting file"""
        self.validate_file(file)

        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower() if file.filename else ".txt"
        filename = f"job_{user_id}_{file.filename}"
        file_path = self.upload_dir / "job-postings" / filename

        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not save file: {str(e)}"
            )

        return str(file_path)

    def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information"""
        try:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    "filename": os.path.basename(file_path),
                    "size": stat.st_size,
                    "created_at": stat.st_ctime,
                    "modified_at": stat.st_mtime
                }
            return None
        except Exception:
            return None

# Global instance
file_upload_service = FileUploadService()