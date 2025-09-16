import re
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict, Counter
from .enhanced_nlp import EnhancedNLPService

class JobAnalysisService:
    """Advanced job posting analysis service"""

    def __init__(self):
        self.nlp_service = EnhancedNLPService()

        # Job posting section indicators
        self.section_indicators = {
            'requirements': [
                'requirements', 'required', 'must have', 'essential', 'mandatory',
                'qualifications', 'prerequisites', 'minimum qualifications'
            ],
            'preferred': [
                'preferred', 'nice to have', 'bonus', 'plus', 'advantageous',
                'desirable', 'preferred qualifications', 'ideal candidate'
            ],
            'responsibilities': [
                'responsibilities', 'duties', 'role', 'what you will do',
                'key responsibilities', 'main duties', 'primary responsibilities'
            ],
            'benefits': [
                'benefits', 'perks', 'compensation', 'what we offer',
                'employee benefits', 'package', 'rewards'
            ]
        }

        # Experience level indicators
        self.experience_patterns = {
            'entry': [
                r'entry.?level', r'0.?2 years', r'new grad', r'graduate',
                r'junior', r'associate', r'trainee'
            ],
            'mid': [
                r'2.?5 years', r'3.?7 years', r'mid.?level', r'intermediate',
                r'experienced', r'professional'
            ],
            'senior': [
                r'5\+ years', r'7\+ years', r'senior', r'lead', r'principal',
                r'expert', r'advanced', r'10\+ years'
            ],
            'executive': [
                r'director', r'manager', r'head of', r'chief', r'vp',
                r'vice president', r'c.?level', r'executive'
            ]
        }

        # Salary indicators
        self.salary_patterns = [
            r'\$(\d{2,3}),?(\d{3})\s*-\s*\$(\d{2,3}),?(\d{3})',  # $80,000 - $120,000
            r'\$(\d{2,3})k?\s*-\s*\$?(\d{2,3})k',  # $80k - $120k
            r'(\d{2,3}),?(\d{3})\s*-\s*(\d{2,3}),?(\d{3})',  # 80,000 - 120,000
            r'\$(\d{2,3}),?(\d{3})',  # $100,000
            r'(\d{2,3})k\s*salary'  # 100k salary
        ]

        # Industry keywords
        self.industry_keywords = {
            'technology': [
                'software', 'tech', 'it', 'development', 'engineering',
                'startup', 'saas', 'platform', 'api', 'cloud', 'ai', 'ml'
            ],
            'finance': [
                'finance', 'banking', 'investment', 'trading', 'fintech',
                'hedge fund', 'private equity', 'wealth management'
            ],
            'healthcare': [
                'healthcare', 'medical', 'hospital', 'clinical', 'pharma',
                'biotech', 'health tech', 'telemedicine'
            ],
            'consulting': [
                'consulting', 'advisory', 'strategy', 'management consulting',
                'consulting firm', 'professional services'
            ],
            'ecommerce': [
                'ecommerce', 'e-commerce', 'retail', 'marketplace',
                'online store', 'digital commerce'
            ]
        }

        # Remote work indicators
        self.remote_keywords = [
            'remote', 'work from home', 'distributed', 'telecommute',
            'virtual', 'anywhere', 'location independent'
        ]

    def analyze_job_posting(self, job_text: str) -> Dict[str, Any]:
        """Comprehensive job posting analysis"""
        analysis = {
            "sections": self._extract_sections(job_text),
            "requirements": self._extract_requirements(job_text),
            "skills": self._extract_job_skills(job_text),
            "experience": self._extract_experience_requirements(job_text),
            "education": self._extract_education_requirements(job_text),
            "salary": self._extract_salary_info(job_text),
            "industry": self._detect_industry(job_text),
            "company_size": self._estimate_company_size(job_text),
            "remote_work": self._detect_remote_work(job_text),
            "keywords": self._extract_important_keywords(job_text),
            "job_level": self._determine_job_level(job_text),
            "urgency": self._assess_urgency(job_text)
        }

        # Calculate job complexity score
        analysis["complexity_score"] = self._calculate_complexity_score(analysis)

        return analysis

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract different sections from job posting"""
        sections = {}
        text_lower = text.lower()

        for section_type, indicators in self.section_indicators.items():
            section_content = ""

            # Find section headers
            for indicator in indicators:
                pattern = rf'({indicator}:?)(.*?)(?=\n\s*[A-Z][^:]*:|\n\s*\n|\Z)'
                matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)

                if matches:
                    # Take the longest match (most detailed section)
                    section_content = max([match[1].strip() for match in matches], key=len)
                    break

            sections[section_type] = section_content

        return sections

    def _extract_requirements(self, text: str) -> Dict[str, List[str]]:
        """Extract required vs preferred qualifications"""
        requirements = {
            "required": [],
            "preferred": [],
            "all": []
        }

        # Split text into sentences
        sentences = re.split(r'[.!?\n]', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue

            sentence_lower = sentence.lower()

            # Check if sentence contains requirements
            is_requirement = any(keyword in sentence_lower for keyword in [
                'require', 'must', 'need', 'essential', 'mandatory', 'necessary'
            ])

            is_preferred = any(keyword in sentence_lower for keyword in [
                'prefer', 'nice', 'bonus', 'plus', 'ideal', 'advantage'
            ])

            if is_requirement:
                requirements["required"].append(sentence)
                requirements["all"].append(sentence)
            elif is_preferred:
                requirements["preferred"].append(sentence)
                requirements["all"].append(sentence)
            elif any(skill_word in sentence_lower for skill_word in [
                'experience', 'knowledge', 'skill', 'ability', 'proficiency'
            ]):
                requirements["all"].append(sentence)

        return requirements

    def _extract_job_skills(self, text: str) -> Dict[str, Any]:
        """Extract skills with context and priority"""
        # Use enhanced NLP service for skill extraction
        skill_analysis = self.nlp_service.enhanced_extract_skills(text)

        # Determine skill priority based on context
        prioritized_skills = self._prioritize_skills(text, skill_analysis["skills"])

        return {
            "by_category": skill_analysis["skills"],
            "confidence_scores": skill_analysis["confidence_scores"],
            "prioritized": prioritized_skills,
            "total_count": skill_analysis["total_skills_found"]
        }

    def _prioritize_skills(self, text: str, skills_by_category: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Prioritize skills based on context in job posting"""
        text_lower = text.lower()
        prioritized = {"critical": [], "important": [], "nice_to_have": []}

        all_skills = []
        for category_skills in skills_by_category.values():
            all_skills.extend(category_skills)

        for skill in all_skills:
            skill_lower = skill.lower()

            # Count mentions and check context
            mention_count = len(re.findall(rf'\b{re.escape(skill_lower)}\b', text_lower))

            # Check if skill appears in critical contexts
            critical_contexts = [
                'required', 'must have', 'essential', 'mandatory',
                'minimum', 'necessary', 'critical'
            ]

            nice_contexts = [
                'preferred', 'nice to have', 'bonus', 'plus', 'ideal'
            ]

            context_score = 0
            for context in critical_contexts:
                if re.search(rf'{context}.*{re.escape(skill_lower)}|{re.escape(skill_lower)}.*{context}', text_lower):
                    context_score += 2

            for context in nice_contexts:
                if re.search(rf'{context}.*{re.escape(skill_lower)}|{re.escape(skill_lower)}.*{context}', text_lower):
                    context_score -= 1

            # Prioritize based on mentions and context
            if mention_count >= 3 or context_score >= 2:
                prioritized["critical"].append(skill)
            elif mention_count >= 2 or context_score >= 1:
                prioritized["important"].append(skill)
            else:
                prioritized["nice_to_have"].append(skill)

        return prioritized

    def _extract_experience_requirements(self, text: str) -> Dict[str, Any]:
        """Extract experience requirements"""
        experience = {
            "years_required": None,
            "level": "unknown",
            "specific_requirements": []
        }

        # Extract years of experience
        years_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'minimum\s*(?:of\s*)?(\d+)\s*years?',
            r'at least\s*(\d+)\s*years?',
            r'(\d+)\s*to\s*(\d+)\s*years?'
        ]

        for pattern in years_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                if isinstance(matches[0], tuple):
                    # Range pattern (e.g., "3 to 5 years")
                    experience["years_required"] = int(matches[0][1])  # Take upper bound
                else:
                    years = [int(match) for match in matches]
                    experience["years_required"] = max(years)

        # Determine experience level
        text_lower = text.lower()
        level_scores = defaultdict(int)

        for level, patterns in self.experience_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                level_scores[level] += matches

        if level_scores:
            experience["level"] = max(level_scores.items(), key=lambda x: x[1])[0]

        return experience

    def _extract_education_requirements(self, text: str) -> Dict[str, Any]:
        """Extract education requirements"""
        education = {
            "degree_required": False,
            "level": "unknown",
            "fields": [],
            "requirements": []
        }

        text_lower = text.lower()

        # Check if degree is required
        degree_required_patterns = [
            r'bachelor.*required', r'degree.*required', r'university.*required',
            r'must.*degree', r'required.*degree'
        ]

        for pattern in degree_required_patterns:
            if re.search(pattern, text_lower):
                education["degree_required"] = True
                break

        # Extract degree level
        degree_levels = {
            'high_school': ['high school', 'diploma', 'ged'],
            'associates': ['associates', 'associate degree', 'aa', 'as'],
            'bachelors': ['bachelors', 'bachelor', 'bs', 'ba', 'btech', 'undergraduate'],
            'masters': ['masters', 'master', 'ms', 'ma', 'mba', 'graduate'],
            'phd': ['phd', 'ph.d', 'doctorate', 'doctoral']
        }

        for level, keywords in degree_levels.items():
            for keyword in keywords:
                if keyword in text_lower:
                    education["level"] = level
                    break

        # Extract field of study
        field_patterns = [
            r'degree in ([a-zA-Z\s]+)',
            r'([a-zA-Z\s]+) degree',
            r'major in ([a-zA-Z\s]+)',
            r'studied ([a-zA-Z\s]+)'
        ]

        for pattern in field_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            education["fields"].extend([match.strip() for match in matches])

        return education

    def _extract_salary_info(self, text: str) -> Dict[str, Any]:
        """Extract salary information"""
        salary_info = {
            "range_found": False,
            "min_salary": None,
            "max_salary": None,
            "currency": "USD",
            "frequency": "annual"
        }

        for pattern in self.salary_patterns:
            matches = re.findall(pattern, text)
            if matches:
                salary_info["range_found"] = True
                # Process the first match found
                match = matches[0]
                if len(match) >= 4:  # Range format
                    salary_info["min_salary"] = int(match[0]) * 1000 + int(match[1])
                    salary_info["max_salary"] = int(match[2]) * 1000 + int(match[3])
                elif len(match) >= 2:  # Single salary or k format
                    if 'k' in text.lower():
                        salary_info["min_salary"] = int(match[0]) * 1000
                    else:
                        salary_info["min_salary"] = int(match[0]) * 1000 + int(match[1])
                break

        return salary_info

    def _detect_industry(self, text: str) -> Dict[str, Any]:
        """Detect industry based on keywords"""
        text_lower = text.lower()
        industry_scores = defaultdict(int)

        for industry, keywords in self.industry_keywords.items():
            for keyword in keywords:
                count = len(re.findall(rf'\b{keyword}\b', text_lower))
                industry_scores[industry] += count

        detected_industry = "unknown"
        if industry_scores:
            detected_industry = max(industry_scores.items(), key=lambda x: x[1])[0]

        return {
            "primary": detected_industry,
            "scores": dict(industry_scores),
            "confidence": max(industry_scores.values()) if industry_scores else 0
        }

    def _estimate_company_size(self, text: str) -> str:
        """Estimate company size based on indicators"""
        text_lower = text.lower()

        startup_indicators = ['startup', 'early stage', 'seed', 'series a', 'fast-paced']
        large_corp_indicators = ['fortune 500', 'multinational', 'enterprise', 'global', 'established']
        medium_indicators = ['growing company', 'scale-up', 'mid-size', 'expanding team']

        if any(indicator in text_lower for indicator in startup_indicators):
            return "startup"
        elif any(indicator in text_lower for indicator in large_corp_indicators):
            return "large_corporation"
        elif any(indicator in text_lower for indicator in medium_indicators):
            return "medium"
        else:
            return "unknown"

    def _detect_remote_work(self, text: str) -> Dict[str, Any]:
        """Detect remote work options"""
        text_lower = text.lower()

        remote_score = 0
        for keyword in self.remote_keywords:
            if keyword in text_lower:
                remote_score += 1

        hybrid_keywords = ['hybrid', 'flexible', 'mix of remote', 'some remote']
        hybrid_score = sum(1 for keyword in hybrid_keywords if keyword in text_lower)

        onsite_keywords = ['on-site', 'in-office', 'office-based', 'no remote']
        onsite_score = sum(1 for keyword in onsite_keywords if keyword in text_lower)

        if remote_score > hybrid_score and remote_score > onsite_score:
            work_type = "remote"
        elif hybrid_score > 0:
            work_type = "hybrid"
        elif onsite_score > 0:
            work_type = "onsite"
        else:
            work_type = "unknown"

        return {
            "type": work_type,
            "remote_score": remote_score,
            "hybrid_score": hybrid_score,
            "onsite_score": onsite_score
        }

    def _extract_important_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """Extract most important keywords from job posting"""
        # Use enhanced NLP service
        keyword_analysis = self.nlp_service.calculate_advanced_keyword_density(text, [])

        # Get all words and their frequencies
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = Counter(words)

        # Filter out common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must',
            'this', 'that', 'these', 'those', 'you', 'your', 'our', 'we', 'they'
        }

        # Filter and get top keywords
        filtered_keywords = {word: freq for word, freq in word_freq.items()
                           if word not in stop_words and len(word) > 3}

        top_keywords = sorted(filtered_keywords.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in top_keywords[:top_n]]

    def _determine_job_level(self, text: str) -> str:
        """Determine overall job level"""
        text_lower = text.lower()

        # Score different levels
        level_indicators = {
            'entry': ['entry', 'junior', 'associate', 'trainee', '0-2 years'],
            'mid': ['mid', 'intermediate', '3-5 years', 'experienced'],
            'senior': ['senior', 'lead', 'principal', '5+ years', 'expert'],
            'executive': ['director', 'manager', 'head', 'chief', 'vp']
        }

        level_scores = defaultdict(int)
        for level, indicators in level_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    level_scores[level] += 1

        if level_scores:
            return max(level_scores.items(), key=lambda x: x[1])[0]
        return "unknown"

    def _assess_urgency(self, text: str) -> Dict[str, Any]:
        """Assess hiring urgency"""
        text_lower = text.lower()

        urgent_keywords = [
            'urgent', 'asap', 'immediately', 'right away', 'start immediately',
            'fast hire', 'quick start', 'emergency', 'critical need'
        ]

        moderate_keywords = [
            'soon', 'quick', 'fast-paced', 'growing team', 'expanding'
        ]

        urgent_score = sum(1 for keyword in urgent_keywords if keyword in text_lower)
        moderate_score = sum(1 for keyword in moderate_keywords if keyword in text_lower)

        if urgent_score > 0:
            urgency = "high"
        elif moderate_score > 0:
            urgency = "moderate"
        else:
            urgency = "normal"

        return {
            "level": urgency,
            "urgent_indicators": urgent_score,
            "moderate_indicators": moderate_score
        }

    def _calculate_complexity_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate job complexity score (0-100)"""
        score = 0

        # Skills complexity (0-30 points)
        total_skills = analysis["skills"]["total_count"]
        if total_skills >= 20:
            score += 30
        elif total_skills >= 10:
            score += 20
        elif total_skills >= 5:
            score += 10

        # Experience requirements (0-25 points)
        years_required = analysis["experience"]["years_required"]
        if years_required:
            if years_required >= 8:
                score += 25
            elif years_required >= 5:
                score += 20
            elif years_required >= 3:
                score += 15
            else:
                score += 10

        # Education requirements (0-15 points)
        if analysis["education"]["degree_required"]:
            edu_level = analysis["education"]["level"]
            if edu_level == "phd":
                score += 15
            elif edu_level == "masters":
                score += 12
            elif edu_level == "bachelors":
                score += 8
            else:
                score += 5

        # Job level (0-20 points)
        job_level = analysis["job_level"]
        if job_level == "executive":
            score += 20
        elif job_level == "senior":
            score += 15
        elif job_level == "mid":
            score += 10
        else:
            score += 5

        # Industry complexity (0-10 points)
        if analysis["industry"]["primary"] in ["technology", "finance"]:
            score += 10
        elif analysis["industry"]["primary"] != "unknown":
            score += 5

        return min(score, 100)  # Cap at 100

# Global instance
job_analysis_service = JobAnalysisService()