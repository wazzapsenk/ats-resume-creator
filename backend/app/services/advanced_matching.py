import re
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict
import math
from difflib import SequenceMatcher
from .enhanced_nlp import EnhancedNLPService
from .job_analysis import JobAnalysisService

class AdvancedMatchingService:
    """Advanced resume-job matching with ML-inspired scoring"""

    def __init__(self):
        self.nlp_service = EnhancedNLPService()
        self.job_service = JobAnalysisService()

        # Skill importance weights by category
        self.category_weights = {
            "programming_languages": 1.0,
            "web_frameworks": 0.9,
            "databases": 0.8,
            "cloud_platforms": 0.8,
            "tools_and_software": 0.6,
            "soft_skills": 0.7
        }

        # Experience matching parameters
        self.experience_decay_factor = 0.1  # How much over-qualification reduces score
        self.experience_bonus_factor = 0.2  # Bonus for exceeding requirements

        # Education level hierarchy for scoring
        self.education_hierarchy = {
            'high_school': 1,
            'certificate': 2,
            'associates': 3,
            'bachelors': 4,
            'masters': 5,
            'phd': 6
        }

    def comprehensive_match_analysis(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any],
        resume_text: str,
        job_text: str
    ) -> Dict[str, Any]:
        """Perform comprehensive matching analysis"""

        # Enhanced skill extraction and analysis
        resume_skills = self.nlp_service.enhanced_extract_skills(resume_text)
        job_analysis = self.job_service.analyze_job_posting(job_text)

        # Calculate detailed matching scores
        skills_analysis = self._advanced_skills_matching(
            resume_skills, job_analysis["skills"]
        )

        experience_analysis = self._experience_matching_analysis(
            resume_data, job_analysis["experience"], resume_text
        )

        education_analysis = self._education_matching_analysis(
            resume_data, job_analysis["education"]
        )

        keyword_analysis = self._advanced_keyword_matching(
            resume_text, job_text, job_analysis["keywords"]
        )

        # ATS compatibility check
        ats_analysis = self.nlp_service.assess_ats_compatibility(resume_text, resume_data)

        # Calculate weighted overall score
        weighted_scores = self._calculate_weighted_scores({
            "skills": skills_analysis["overall_score"],
            "experience": experience_analysis["score"],
            "education": education_analysis["score"],
            "keywords": keyword_analysis["overall_score"],
            "ats": ats_analysis["ats_score"]
        })

        # Generate detailed recommendations
        recommendations = self._generate_detailed_recommendations(
            skills_analysis, experience_analysis, education_analysis,
            keyword_analysis, ats_analysis, job_analysis
        )

        return {
            "overall_score": weighted_scores["total"],
            "match_percentage": weighted_scores["total"],
            "component_scores": {
                "skills_score": skills_analysis["overall_score"],
                "experience_score": experience_analysis["score"],
                "education_score": education_analysis["score"],
                "keywords_score": keyword_analysis["overall_score"],
                "ats_score": ats_analysis["ats_score"]
            },
            "detailed_analysis": {
                "skills": skills_analysis,
                "experience": experience_analysis,
                "education": education_analysis,
                "keywords": keyword_analysis,
                "ats": ats_analysis
            },
            "job_complexity": job_analysis.get("complexity_score", 50),
            "recommendations": recommendations,
            "match_strengths": self._identify_match_strengths(skills_analysis, experience_analysis),
            "improvement_areas": self._identify_improvement_areas(skills_analysis, keyword_analysis)
        }

    def _advanced_skills_matching(
        self,
        resume_skills: Dict[str, Any],
        job_skills: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Advanced skill matching with synonym support and weighting"""

        resume_skills_dict = resume_skills.get("skills", {})
        job_skills_dict = job_skills.get("by_category", {})
        prioritized_job_skills = job_skills.get("prioritized", {})

        analysis = {
            "matched_skills": {},
            "missing_critical_skills": [],
            "missing_important_skills": [],
            "missing_nice_to_have_skills": [],
            "skill_coverage_by_category": {},
            "overall_score": 0,
            "strength_areas": [],
            "weakness_areas": []
        }

        total_score = 0
        total_weight = 0

        # Analyze each skill category
        for category in set(list(resume_skills_dict.keys()) + list(job_skills_dict.keys())):
            resume_category_skills = set(resume_skills_dict.get(category, []))
            job_category_skills = set(job_skills_dict.get(category, []))

            if not job_category_skills:
                continue

            # Calculate matches with synonym support
            matches, partial_matches = self._find_skill_matches_with_synonyms(
                resume_category_skills, job_category_skills, category
            )

            # Calculate category score
            category_weight = self.category_weights.get(category, 0.7)
            exact_match_score = len(matches) / len(job_category_skills) if job_category_skills else 0
            partial_match_bonus = len(partial_matches) * 0.3 / len(job_category_skills) if job_category_skills else 0
            category_score = min(1.0, exact_match_score + partial_match_bonus) * 100

            analysis["matched_skills"][category] = {
                "exact_matches": list(matches),
                "partial_matches": list(partial_matches),
                "missing": list(job_category_skills - matches),
                "coverage_percentage": exact_match_score * 100,
                "category_score": category_score
            }

            analysis["skill_coverage_by_category"][category] = category_score

            # Determine strength/weakness
            if category_score >= 80:
                analysis["strength_areas"].append(category)
            elif category_score < 40:
                analysis["weakness_areas"].append(category)

            # Weight by category importance
            total_score += category_score * category_weight
            total_weight += category_weight

        # Analyze prioritized skills
        self._analyze_prioritized_skills(analysis, resume_skills_dict, prioritized_job_skills)

        # Calculate overall skills score
        analysis["overall_score"] = total_score / total_weight if total_weight > 0 else 0

        return analysis

    def _find_skill_matches_with_synonyms(
        self,
        resume_skills: Set[str],
        job_skills: Set[str],
        category: str
    ) -> Tuple[Set[str], Set[str]]:
        """Find exact and partial matches considering synonyms"""

        exact_matches = set()
        partial_matches = set()

        # Get synonym mapping for this category
        category_data = self.nlp_service.skill_taxonomy.get(category, {})
        synonyms = category_data.get("synonyms", {})

        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()

            # Check for exact matches
            if job_skill_lower in [rs.lower() for rs in resume_skills]:
                exact_matches.add(job_skill)
                continue

            # Check synonyms
            found_synonym = False
            if job_skill_lower in synonyms:
                for synonym in synonyms[job_skill_lower]:
                    if synonym.lower() in [rs.lower() for rs in resume_skills]:
                        exact_matches.add(job_skill)
                        found_synonym = True
                        break

            if found_synonym:
                continue

            # Check reverse synonyms (resume has main skill, job has synonym)
            for main_skill, skill_synonyms in synonyms.items():
                if main_skill.lower() in [rs.lower() for rs in resume_skills]:
                    if job_skill_lower in [s.lower() for s in skill_synonyms]:
                        exact_matches.add(job_skill)
                        found_synonym = True
                        break

            if found_synonym:
                continue

            # Check for partial matches (fuzzy matching)
            for resume_skill in resume_skills:
                similarity = SequenceMatcher(None, job_skill_lower, resume_skill.lower()).ratio()
                if similarity >= 0.8:  # 80% similarity threshold
                    partial_matches.add(job_skill)
                    break

        return exact_matches, partial_matches

    def _analyze_prioritized_skills(
        self,
        analysis: Dict[str, Any],
        resume_skills: Dict[str, List[str]],
        prioritized_job_skills: Dict[str, List[str]]
    ) -> None:
        """Analyze critical, important, and nice-to-have skills"""

        all_resume_skills = set()
        for skills_list in resume_skills.values():
            all_resume_skills.update([skill.lower() for skill in skills_list])

        for priority, skills in prioritized_job_skills.items():
            missing_skills = []
            for skill in skills:
                if skill.lower() not in all_resume_skills:
                    # Check for synonyms
                    found = False
                    for category_data in self.nlp_service.skill_taxonomy.values():
                        synonyms = category_data.get("synonyms", {})
                        if skill.lower() in synonyms:
                            for synonym in synonyms[skill.lower()]:
                                if synonym.lower() in all_resume_skills:
                                    found = True
                                    break
                        if found:
                            break

                    if not found:
                        missing_skills.append(skill)

            if priority == "critical":
                analysis["missing_critical_skills"] = missing_skills
            elif priority == "important":
                analysis["missing_important_skills"] = missing_skills
            else:
                analysis["missing_nice_to_have_skills"] = missing_skills

    def _experience_matching_analysis(
        self,
        resume_data: Dict[str, Any],
        job_experience: Dict[str, Any],
        resume_text: str
    ) -> Dict[str, Any]:
        """Analyze experience matching with nuanced scoring"""

        # Extract resume experience
        resume_experience = self.nlp_service.enhanced_extract_experience(resume_text)

        analysis = {
            "score": 0,
            "resume_years": resume_experience.get("total_years", 0),
            "required_years": job_experience.get("years_required", 0),
            "level_match": False,
            "experience_gap": 0,
            "analysis_details": {}
        }

        required_years = job_experience.get("years_required", 0)
        resume_years = resume_experience.get("total_years", 0)

        if required_years == 0:
            # No specific experience requirement
            analysis["score"] = 80  # Neutral score
        else:
            if resume_years >= required_years:
                # Meets or exceeds requirement
                excess_years = resume_years - required_years
                if excess_years <= 2:
                    # Perfect match or slight over-qualification
                    analysis["score"] = 90 + min(excess_years * 5, 10)
                else:
                    # Over-qualified (might be seen as negative)
                    penalty = min(excess_years * self.experience_decay_factor, 20)
                    analysis["score"] = 90 - penalty
            else:
                # Under-qualified
                gap = required_years - resume_years
                analysis["experience_gap"] = gap
                if gap <= 1:
                    analysis["score"] = 70  # Close enough
                elif gap <= 2:
                    analysis["score"] = 50  # Noticeable gap
                else:
                    analysis["score"] = max(20, 50 - (gap * 10))  # Significant gap

        # Level matching
        resume_level = resume_experience.get("seniority_level", "unknown")
        job_level = job_experience.get("level", "unknown")

        if resume_level != "unknown" and job_level != "unknown":
            level_hierarchy = {"entry": 1, "mid": 2, "senior": 3, "executive": 4}
            resume_level_score = level_hierarchy.get(resume_level, 2)
            job_level_score = level_hierarchy.get(job_level, 2)

            if resume_level_score == job_level_score:
                analysis["level_match"] = True
                analysis["score"] += 5  # Bonus for level match
            elif abs(resume_level_score - job_level_score) == 1:
                analysis["score"] += 2  # Small bonus for close level
            elif resume_level_score < job_level_score - 1:
                analysis["score"] -= 10  # Penalty for significant under-level

        analysis["analysis_details"] = {
            "resume_seniority": resume_level,
            "job_seniority": job_level,
            "years_comparison": f"{resume_years} vs {required_years} required",
            "qualification_status": "over-qualified" if resume_years > required_years + 2
                                   else "qualified" if resume_years >= required_years
                                   else "under-qualified"
        }

        return analysis

    def _education_matching_analysis(
        self,
        resume_data: Dict[str, Any],
        job_education: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze education matching"""

        analysis = {
            "score": 50,  # Default neutral score
            "degree_requirement_met": False,
            "level_comparison": {},
            "field_match": False
        }

        # Extract resume education from structured data
        resume_education = resume_data.get("education", [])
        if not resume_education:
            return analysis

        # Get highest education level from resume
        resume_highest = "unknown"
        for edu in resume_education:
            if isinstance(edu, dict):
                degree = edu.get("degree", "").lower()
                for level, keywords in self.nlp_service.education_levels.items():
                    if any(keyword in degree for keyword in keywords):
                        if (resume_highest == "unknown" or
                            self.education_hierarchy.get(level, 0) >
                            self.education_hierarchy.get(resume_highest, 0)):
                            resume_highest = level

        job_required_level = job_education.get("level", "unknown")
        degree_required = job_education.get("degree_required", False)

        if degree_required and resume_highest != "unknown":
            analysis["degree_requirement_met"] = True
            analysis["score"] = 70  # Base score for having a degree

            # Compare levels
            resume_hierarchy_score = self.education_hierarchy.get(resume_highest, 0)
            job_hierarchy_score = self.education_hierarchy.get(job_required_level, 0)

            if job_hierarchy_score > 0:
                if resume_hierarchy_score >= job_hierarchy_score:
                    # Meets or exceeds requirement
                    analysis["score"] = 85 + min((resume_hierarchy_score - job_hierarchy_score) * 5, 15)
                else:
                    # Below requirement
                    gap = job_hierarchy_score - resume_hierarchy_score
                    analysis["score"] = max(40, 70 - (gap * 15))

            analysis["level_comparison"] = {
                "resume_level": resume_highest,
                "required_level": job_required_level,
                "meets_requirement": resume_hierarchy_score >= job_hierarchy_score
            }

        elif not degree_required:
            # No degree required
            analysis["score"] = 80
            analysis["degree_requirement_met"] = True

        # Check field of study match
        job_fields = job_education.get("fields", [])
        if job_fields and resume_education:
            for edu in resume_education:
                if isinstance(edu, dict):
                    resume_field = edu.get("field", "").lower()
                    for job_field in job_fields:
                        if (resume_field and job_field.lower() in resume_field or
                            resume_field in job_field.lower()):
                            analysis["field_match"] = True
                            analysis["score"] += 10  # Bonus for field match
                            break

        return analysis

    def _advanced_keyword_matching(
        self,
        resume_text: str,
        job_text: str,
        job_keywords: List[str]
    ) -> Dict[str, Any]:
        """Advanced keyword matching with context analysis"""

        keyword_analysis = self.nlp_service.calculate_advanced_keyword_density(
            resume_text, job_keywords
        )

        analysis = {
            "overall_score": 0,
            "keyword_coverage": 0,
            "high_density_keywords": [],
            "missing_keywords": [],
            "context_analysis": {},
            "density_distribution": {}
        }

        if not job_keywords:
            analysis["overall_score"] = 50  # Neutral if no keywords to match
            return analysis

        # Analyze keyword coverage and density
        covered_keywords = 0
        total_density_score = 0

        for keyword in job_keywords:
            keyword_data = keyword_analysis["densities"].get(keyword, {})
            count = keyword_data.get("count", 0)
            density = keyword_data.get("density_percentage", 0)

            if count > 0:
                covered_keywords += 1
                # Score based on density (optimal range: 0.5% - 3%)
                if 0.5 <= density <= 3.0:
                    density_score = 100
                elif density < 0.5:
                    density_score = density * 200  # Scale up low densities
                else:
                    density_score = max(50, 100 - (density - 3.0) * 10)  # Penalize keyword stuffing

                total_density_score += density_score

                if density >= 1.0:
                    analysis["high_density_keywords"].append({
                        "keyword": keyword,
                        "density": density,
                        "count": count
                    })
            else:
                analysis["missing_keywords"].append(keyword)

        # Calculate scores
        analysis["keyword_coverage"] = (covered_keywords / len(job_keywords)) * 100
        avg_density_score = total_density_score / covered_keywords if covered_keywords > 0 else 0

        # Overall keyword score (weighted average of coverage and density quality)
        coverage_weight = 0.7
        density_weight = 0.3
        analysis["overall_score"] = (
            analysis["keyword_coverage"] * coverage_weight +
            avg_density_score * density_weight
        )

        # Context analysis
        analysis["context_analysis"] = keyword_analysis.get("context_analysis", {})

        return analysis

    def _calculate_weighted_scores(self, component_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate weighted overall scores"""

        # Weights for different components
        weights = {
            "skills": 0.35,      # Most important
            "experience": 0.25,   # Very important
            "keywords": 0.20,     # Important for ATS
            "education": 0.15,    # Moderately important
            "ats": 0.05          # Baseline requirement
        }

        weighted_total = 0
        total_weight = 0

        weighted_scores = {}

        for component, score in component_scores.items():
            weight = weights.get(component, 0)
            weighted_score = score * weight
            weighted_total += weighted_score
            total_weight += weight

            weighted_scores[f"{component}_weighted"] = weighted_score

        weighted_scores["total"] = weighted_total / total_weight if total_weight > 0 else 0

        return weighted_scores

    def _generate_detailed_recommendations(
        self,
        skills_analysis: Dict[str, Any],
        experience_analysis: Dict[str, Any],
        education_analysis: Dict[str, Any],
        keyword_analysis: Dict[str, Any],
        ats_analysis: Dict[str, Any],
        job_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate detailed, actionable recommendations"""

        recommendations = []

        # Skills recommendations
        if skills_analysis["missing_critical_skills"]:
            recommendations.append({
                "type": "critical_skills",
                "priority": "high",
                "title": "Add Critical Skills",
                "description": f"Focus on acquiring these critical skills: {', '.join(skills_analysis['missing_critical_skills'][:5])}",
                "action_items": [
                    f"Take online courses or certifications in {skill}"
                    for skill in skills_analysis['missing_critical_skills'][:3]
                ]
            })

        # Experience recommendations
        if experience_analysis["experience_gap"] > 0:
            recommendations.append({
                "type": "experience",
                "priority": "high",
                "title": "Bridge Experience Gap",
                "description": f"You need {experience_analysis['experience_gap']} more years of relevant experience",
                "action_items": [
                    "Highlight transferable skills from other experiences",
                    "Consider freelance or volunteer projects",
                    "Emphasize relevant internships or academic projects"
                ]
            })

        # Keyword optimization
        if keyword_analysis["keyword_coverage"] < 60:
            missing_keywords = keyword_analysis["missing_keywords"][:5]
            recommendations.append({
                "type": "keywords",
                "priority": "medium",
                "title": "Improve Keyword Coverage",
                "description": f"Include these keywords: {', '.join(missing_keywords)}",
                "action_items": [
                    "Naturally integrate keywords into your experience descriptions",
                    "Use industry-standard terminology",
                    "Mirror language from the job posting"
                ]
            })

        # ATS optimization
        if ats_analysis["ats_score"] < 70:
            recommendations.extend([
                {
                    "type": "ats_formatting",
                    "priority": "medium",
                    "title": "Improve ATS Compatibility",
                    "description": "Optimize resume format for ATS systems",
                    "action_items": [
                        "Use standard section headers (Experience, Education, Skills)",
                        "Avoid complex formatting and graphics",
                        "Use standard fonts and bullet points",
                        "Include contact information in a clear format"
                    ]
                }
            ])

        # Education recommendations
        if not education_analysis["degree_requirement_met"]:
            recommendations.append({
                "type": "education",
                "priority": "low",
                "title": "Consider Educational Enhancement",
                "description": "This role may prefer candidates with specific educational background",
                "action_items": [
                    "Consider relevant certifications",
                    "Highlight relevant coursework or training",
                    "Emphasize practical experience that compensates"
                ]
            })

        return recommendations

    def _identify_match_strengths(
        self,
        skills_analysis: Dict[str, Any],
        experience_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify key strengths in the match"""

        strengths = []

        # Skill strengths
        strength_areas = skills_analysis.get("strength_areas", [])
        if strength_areas:
            strengths.append(f"Strong skills in: {', '.join(strength_areas)}")

        # Experience strengths
        if experience_analysis["score"] >= 80:
            qualification_status = experience_analysis["analysis_details"]["qualification_status"]
            strengths.append(f"Experience level: {qualification_status}")

        if experience_analysis.get("level_match", False):
            strengths.append("Seniority level matches job requirements")

        return strengths

    def _identify_improvement_areas(
        self,
        skills_analysis: Dict[str, Any],
        keyword_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify key areas for improvement"""

        improvements = []

        # Skill gaps
        weakness_areas = skills_analysis.get("weakness_areas", [])
        if weakness_areas:
            improvements.append(f"Develop skills in: {', '.join(weakness_areas)}")

        # Critical missing skills
        critical_missing = skills_analysis.get("missing_critical_skills", [])
        if critical_missing:
            improvements.append(f"Acquire critical skills: {', '.join(critical_missing[:3])}")

        # Keyword coverage
        if keyword_analysis["keyword_coverage"] < 50:
            improvements.append("Improve keyword optimization and industry terminology usage")

        return improvements

# Global instance
advanced_matching_service = AdvancedMatchingService()