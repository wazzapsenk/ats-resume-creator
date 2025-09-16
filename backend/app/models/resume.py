from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import Base, TimestampMixin

class ResumeStatus(PyEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(Enum(ResumeStatus), default=ResumeStatus.DRAFT)

    # Personal Information
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)

    # Resume Content (JSON format for flexibility)
    summary = Column(Text, nullable=True)
    work_experience = Column(JSON, nullable=True)  # List of experience objects
    education = Column(JSON, nullable=True)  # List of education objects
    skills = Column(JSON, nullable=True)  # List of skills with categories
    certifications = Column(JSON, nullable=True)  # List of certification objects
    projects = Column(JSON, nullable=True)  # List of project objects
    languages = Column(JSON, nullable=True)  # List of language objects

    # File references
    original_file_path = Column(String(500), nullable=True)  # If uploaded from file
    generated_pdf_path = Column(String(500), nullable=True)  # Generated LaTeX PDF

    # Parsed content
    raw_text = Column(Text, nullable=True)  # Extracted text for NLP processing

    # Relationships
    user = relationship("User", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resume(title='{self.title}', user_id={self.user_id})>"