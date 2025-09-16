from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class JobPostingBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    seniority_level: Optional[str] = None
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None

class JobPostingCreate(JobPostingBase):
    source_url: Optional[str] = None
    source_platform: Optional[str] = None

class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    seniority_level: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    source_url: Optional[str] = None
    source_platform: Optional[str] = None

class JobPostingResponse(JobPostingBase):
    id: int
    user_id: int
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education_level: Optional[str] = None
    industry: Optional[str] = None
    keywords: Optional[List[str]] = None
    source_url: Optional[str] = None
    source_platform: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True