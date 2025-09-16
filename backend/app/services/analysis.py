from typing import Dict, List, Any, Optional, Tuple
import time
from sqlalchemy.orm import Session
from ..models.resume import Resume
from ..models.job_posting import JobPosting
from ..models.analysis import Analysis, AnalysisStatus
from .basic_nlp import basic_nlp_service

class AnalysisService:
    """Service for analyzing resume-job posting compatibility"""

    def __init__(self):
        self.algorithm_version = "2.0.0"
        self.nlp_model_version = "enhanced_1.0"

    def analyze_resume_job_match(
        self,
        resume: Resume,
        job_posting: JobPosting,
        analysis: Analysis,
        db: Session
    ) -> Analysis:
        """
        Perform comprehensive analysis of resume-job posting match using enhanced NLP
        """
        start_time = time.time()

        try:
            # Update status to processing
            analysis.status = AnalysisStatus.PROCESSING
            db.commit()

            # Prepare resume data
            resume_data = self._prepare_resume_data(resume)
            resume_text = self._get_resume_text(resume)

            # Prepare job posting data
            job_text = self._get_job_posting_text(job_posting)

            # Perform basic analysis
            match_results = basic_nlp_service.calculate_match_score(resume_text, job_text)

            # Update analysis with comprehensive results
            processing_time = time.time() - start_time

            analysis.status = AnalysisStatus.COMPLETED
            analysis.overall_score = match_results["overall_score"]
            analysis.match_percentage = match_results["skill_match_percentage"]

            # Component scores
            analysis.skills_score = match_results["skill_match_percentage"]
            analysis.experience_score = 75.0  # Placeholder
            analysis.education_score = 80.0   # Placeholder
            analysis.keywords_score = match_results["text_similarity"] * 100

            # Skills analysis
            all_matched = []
            all_missing = []
            for category, skills in match_results["matched_skills"].items():
                all_matched.extend(skills)
            for category, skills in match_results["missing_skills"].items():
                all_missing.extend(skills)

            analysis.matched_skills = all_matched
            analysis.missing_skills = all_missing

            # Experience analysis (simplified)
            analysis.experience_gap = {
                "years_gap": 0,
                "details": "Experience analysis not implemented in simplified version"
            }

            # Keywords analysis (simplified)
            analysis.keyword_analysis = {
                "coverage_percentage": match_results["text_similarity"] * 100,
                "missing_keywords": [],
                "high_density": []
            }

            # Recommendations (simplified)
            suggestions = []
            if all_missing:
                suggestions.append({
                    "type": "skills",
                    "priority": "high",
                    "title": "Add missing skills",
                    "description": f"Consider adding these skills: {', '.join(all_missing[:5])}"
                })

            analysis.suggestions = suggestions
            analysis.missing_keywords = []
            analysis.content_recommendations = [
                {
                    "type": "improvement",
                    "areas": ["Add missing skills", "Improve keyword matching"]
                },
                {
                    "type": "strengths",
                    "areas": ["Good skill match" if all_matched else "Skills need improvement"]
                }
            ]

            # ATS compatibility (simplified)
            analysis.ats_issues = []
            analysis.format_suggestions = [
                "Use standard section headings",
                "Avoid complex formatting",
                "Include relevant keywords"
            ]

            # Metadata
            analysis.processing_time_seconds = processing_time
            analysis.nlp_model_version = self.nlp_model_version
            analysis.analysis_algorithm_version = self.algorithm_version

            db.commit()

        except Exception as e:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            db.commit()

        return analysis

    def _prepare_resume_data(self, resume: Resume) -> Dict[str, Any]:
        """Prepare resume data for analysis"""
        return {
            "work_experience": resume.work_experience or [],
            "education": resume.education or [],
            "skills": resume.skills or [],
            "certifications": resume.certifications or [],
            "projects": resume.projects or [],
            "languages": resume.languages or []
        }

    def _get_resume_text(self, resume: Resume) -> str:
        """Extract complete resume text"""
        if resume.raw_text:
            return resume.raw_text

        # Combine all structured data into text
        text_parts = []
        if resume.summary:
            text_parts.append(resume.summary)

        if resume.work_experience:
            for exp in resume.work_experience:
                if isinstance(exp, dict):
                    text_parts.extend([str(v) for v in exp.values() if v])

        if resume.education:
            for edu in resume.education:
                if isinstance(edu, dict):
                    text_parts.extend([str(v) for v in edu.values() if v])

        if resume.skills:
            for skill in resume.skills:
                if isinstance(skill, dict):
                    text_parts.extend([str(v) for v in skill.values() if v])

        return " ".join(text_parts)

    def _get_job_posting_text(self, job_posting: JobPosting) -> str:
        """Extract complete job posting text"""
        text_parts = [job_posting.description]
        if job_posting.requirements:
            text_parts.append(job_posting.requirements)
        if job_posting.responsibilities:
            text_parts.append(job_posting.responsibilities)
        if job_posting.benefits:
            text_parts.append(job_posting.benefits)

        return " ".join(filter(None, text_parts))

    def _analyze_resume(self, resume: Resume) -> Dict[str, Any]:
        """Analyze resume content"""
        resume_text = resume.raw_text or ""

        # If no raw text, extract from structured data
        if not resume_text and resume.summary:
            resume_text = resume.summary

        if not resume_text:
            # Combine all text fields
            text_parts = []
            if resume.summary:
                text_parts.append(resume.summary)
            if resume.work_experience:
                for exp in resume.work_experience:
                    if isinstance(exp, dict):
                        text_parts.extend([str(v) for v in exp.values() if v])
            if resume.education:
                for edu in resume.education:
                    if isinstance(edu, dict):
                        text_parts.extend([str(v) for v in edu.values() if v])

            resume_text = " ".join(text_parts)

        # Extract information
        skills = text_processing_service.extract_skills(resume_text)
        keywords = text_processing_service.extract_keywords(resume_text)
        contact_info = text_processing_service.extract_contact_info(resume_text)

        return {
            "text": resume_text,
            "skills": skills,
            "keywords": keywords,
            "contact_info": contact_info,
            "structured_data": {
                "work_experience": resume.work_experience or [],
                "education": resume.education or [],
                "skills_structured": resume.skills or [],
                "certifications": resume.certifications or [],
                "projects": resume.projects or []
            }
        }

    def _analyze_job_posting(self, job_posting: JobPosting) -> Dict[str, Any]:
        """Analyze job posting content"""
        # Combine all job posting text
        text_parts = [job_posting.description]
        if job_posting.requirements:
            text_parts.append(job_posting.requirements)
        if job_posting.responsibilities:
            text_parts.append(job_posting.responsibilities)

        job_text = " ".join(filter(None, text_parts))

        # Extract information
        skills = text_processing_service.extract_skills(job_text)
        keywords = text_processing_service.extract_keywords(job_text)

        return {
            "text": job_text,
            "skills": skills,
            "keywords": keywords,
            "structured_data": {
                "required_skills": job_posting.required_skills or [],
                "preferred_skills": job_posting.preferred_skills or [],
                "experience_years": job_posting.experience_years,
                "education_level": job_posting.education_level,
                "industry": job_posting.industry
            }
        }

    def _perform_matching_analysis(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform basic matching analysis"""

        # Skills matching
        resume_skills = self._flatten_skills(resume_data["skills"])
        job_skills = self._flatten_skills(job_data["skills"])

        matched_skills = list(set(resume_skills) & set(job_skills))
        missing_skills = list(set(job_skills) - set(resume_skills))

        skills_score = (len(matched_skills) / max(len(job_skills), 1)) * 100

        # Keywords matching
        resume_keywords = set(resume_data["keywords"])
        job_keywords = set(job_data["keywords"])

        matched_keywords = list(resume_keywords & job_keywords)
        missing_keywords = list(job_keywords - resume_keywords)

        keywords_score = (len(matched_keywords) / max(len(job_keywords), 1)) * 100

        # Basic experience and education scoring (simplified)
        experience_score = 75.0  # Placeholder
        education_score = 80.0   # Placeholder

        # Overall score calculation
        weights = {
            "skills": 0.4,
            "keywords": 0.3,
            "experience": 0.2,
            "education": 0.1
        }

        overall_score = (
            skills_score * weights["skills"] +
            keywords_score * weights["keywords"] +
            experience_score * weights["experience"] +
            education_score * weights["education"]
        )

        match_percentage = min(overall_score, 100.0)

        return {
            "overall_score": round(overall_score, 2),
            "match_percentage": round(match_percentage, 2),
            "skills_score": round(skills_score, 2),
            "experience_score": round(experience_score, 2),
            "education_score": round(education_score, 2),
            "keywords_score": round(keywords_score, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "experience_gap": {"message": "Experience analysis not yet implemented"},
            "keyword_analysis": {
                "matched_keywords": matched_keywords,
                "missing_keywords": missing_keywords,
                "keyword_density": {}
            }
        }

    def _generate_suggestions(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any],
        match_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate improvement suggestions"""

        suggestions = []
        missing_keywords = match_results["keyword_analysis"]["missing_keywords"]
        missing_skills = match_results["missing_skills"]

        # Skills suggestions
        if missing_skills:
            suggestions.append({
                "type": "skills",
                "priority": "high",
                "title": "Add missing technical skills",
                "description": f"Consider adding these skills to your resume: {', '.join(missing_skills[:5])}"
            })

        # Keywords suggestions
        if missing_keywords:
            suggestions.append({
                "type": "keywords",
                "priority": "medium",
                "title": "Optimize keywords",
                "description": f"Include these keywords in your resume: {', '.join(missing_keywords[:5])}"
            })

        # ATS optimization
        suggestions.append({
            "type": "formatting",
            "priority": "medium",
            "title": "ATS optimization",
            "description": "Use standard section headings and avoid complex formatting"
        })

        content_recommendations = [
            {
                "section": "summary",
                "suggestion": "Tailor your summary to include job-specific keywords"
            },
            {
                "section": "experience",
                "suggestion": "Quantify your achievements with specific metrics"
            }
        ]

        return {
            "improvement_suggestions": suggestions,
            "missing_keywords": missing_keywords[:10],  # Top 10
            "content_recommendations": content_recommendations
        }

    def _analyze_ats_compatibility(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ATS compatibility"""
        issues = []
        suggestions = []

        # Basic ATS checks
        text = resume_data["text"]

        # Check for contact information
        contact_info = resume_data["contact_info"]
        if not contact_info["email"]:
            issues.append({
                "type": "missing_contact",
                "severity": "high",
                "description": "Email address not clearly identified"
            })

        if not contact_info["phone"]:
            issues.append({
                "type": "missing_contact",
                "severity": "medium",
                "description": "Phone number not clearly identified"
            })

        # Check text length
        if len(text.split()) < 100:
            issues.append({
                "type": "content_length",
                "severity": "medium",
                "description": "Resume content appears too short"
            })

        # Formatting suggestions
        suggestions.extend([
            {
                "type": "format",
                "description": "Use standard section headings like 'Experience', 'Education', 'Skills'"
            },
            {
                "type": "format",
                "description": "Avoid images, graphics, and complex formatting"
            },
            {
                "type": "content",
                "description": "Use bullet points for easy scanning"
            }
        ])

        return {
            "issues": issues,
            "suggestions": suggestions
        }

    def _flatten_skills(self, skills_dict: Dict[str, List[str]]) -> List[str]:
        """Flatten skills dictionary to a single list"""
        all_skills = []
        for skill_list in skills_dict.values():
            all_skills.extend(skill_list)
        return all_skills

# Global instance
analysis_service = AnalysisService()