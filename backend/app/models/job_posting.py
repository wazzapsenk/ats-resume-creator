from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class JobPosting(Base, TimestampMixin):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Basic Job Information
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    job_type = Column(String(100), nullable=True)  # full-time, part-time, contract, etc.
    seniority_level = Column(String(100), nullable=True)  # entry, mid, senior, etc.

    # Job Content
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)

    # Processed Content (from NLP analysis)
    required_skills = Column(JSON, nullable=True)  # List of required skills
    preferred_skills = Column(JSON, nullable=True)  # List of preferred skills
    experience_years = Column(Float, nullable=True)  # Required years of experience
    education_level = Column(String(100), nullable=True)  # degree requirement
    industry = Column(String(100), nullable=True)  # tech, finance, healthcare, etc.
    keywords = Column(JSON, nullable=True)  # Extracted keywords for matching

    # Source Information
    source_url = Column(String(1000), nullable=True)  # If scraped from job board
    source_platform = Column(String(100), nullable=True)  # LinkedIn, Indeed, etc.

    # Processed text for NLP
    processed_text = Column(Text, nullable=True)  # Cleaned and normalized text

    # Relationships
    user = relationship("User", back_populates="job_postings")
    analyses = relationship("Analysis", back_populates="job_posting", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<JobPosting(title='{self.title}', company='{self.company}')>"