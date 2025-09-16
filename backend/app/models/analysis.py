from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import Base, TimestampMixin

class AnalysisStatus(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Analysis(Base, TimestampMixin):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)

    # Analysis Status
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    error_message = Column(Text, nullable=True)

    # Overall Matching Results
    overall_score = Column(Float, nullable=True)  # 0-100 ATS compatibility score
    match_percentage = Column(Float, nullable=True)  # 0-100 job match percentage

    # Detailed Scoring
    skills_score = Column(Float, nullable=True)  # Skills matching score
    experience_score = Column(Float, nullable=True)  # Experience relevance score
    education_score = Column(Float, nullable=True)  # Education matching score
    keywords_score = Column(Float, nullable=True)  # Keywords density score

    # Matching Analysis (JSON format for detailed results)
    matched_skills = Column(JSON, nullable=True)  # Skills that match
    missing_skills = Column(JSON, nullable=True)  # Required skills not found
    experience_gap = Column(JSON, nullable=True)  # Experience requirements vs. actual
    keyword_analysis = Column(JSON, nullable=True)  # Keyword frequency and matches

    # Improvement Suggestions
    suggestions = Column(JSON, nullable=True)  # List of improvement suggestions
    missing_keywords = Column(JSON, nullable=True)  # Keywords to add
    content_recommendations = Column(JSON, nullable=True)  # Content improvement tips

    # ATS Optimization
    ats_issues = Column(JSON, nullable=True)  # ATS parsing issues found
    format_suggestions = Column(JSON, nullable=True)  # Format improvement suggestions

    # Processing Metadata
    processing_time_seconds = Column(Float, nullable=True)
    nlp_model_version = Column(String(100), nullable=True)
    analysis_algorithm_version = Column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="analyses")
    resume = relationship("Resume", back_populates="analyses")
    job_posting = relationship("JobPosting", back_populates="analyses")

    def __repr__(self):
        return f"<Analysis(id={self.id}, score={self.overall_score}, status='{self.status}')>"