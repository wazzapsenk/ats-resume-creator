from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.analysis import AnalysisStatus

class AnalysisBase(BaseModel):
    resume_id: int
    job_posting_id: int

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisResponse(AnalysisBase):
    id: int
    user_id: int
    status: AnalysisStatus
    error_message: Optional[str] = None

    # Scoring
    overall_score: Optional[float] = None
    match_percentage: Optional[float] = None
    skills_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    keywords_score: Optional[float] = None

    # Analysis Details
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    experience_gap: Optional[Dict[str, Any]] = None
    keyword_analysis: Optional[Dict[str, Any]] = None

    # Suggestions
    suggestions: Optional[List[Dict[str, Any]]] = None
    missing_keywords: Optional[List[str]] = None
    content_recommendations: Optional[List[Dict[str, Any]]] = None

    # ATS Issues
    ats_issues: Optional[List[Dict[str, Any]]] = None
    format_suggestions: Optional[List[Dict[str, Any]]] = None

    # Metadata
    processing_time_seconds: Optional[float] = None
    nlp_model_version: Optional[str] = None
    analysis_algorithm_version: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True