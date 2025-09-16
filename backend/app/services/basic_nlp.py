import re
import string
from typing import Dict, List, Any, Set
from collections import Counter

class BasicNLPService:
    """Very basic NLP service with no external dependencies for ML"""

    def __init__(self):
        # Basic skill keywords
        self.skill_keywords = {
            "programming_languages": [
                "python", "javascript", "java", "c#", "c++", "php", "ruby", "go", "rust",
                "kotlin", "swift", "typescript", "scala", "r", "matlab", "shell", "bash"
            ],
            "web_technologies": [
                "html", "css", "react", "vue", "angular", "node.js", "express", "django",
                "flask", "spring", "laravel", "rails", "asp.net", "bootstrap", "jquery"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis", "elasticsearch",
                "cassandra", "dynamodb", "sql server", "mariadb"
            ],
            "cloud_platforms": [
                "aws", "azure", "google cloud", "heroku", "digitalocean", "docker",
                "kubernetes", "jenkins", "terraform", "ansible"
            ],
            "frameworks": [
                "react", "angular", "vue", "django", "flask", "spring", "laravel",
                "rails", "express", "fastapi", "tensorflow", "pytorch", "pandas", "numpy"
            ],
            "soft_skills": [
                "leadership", "communication", "teamwork", "problem solving", "project management",
                "agile", "scrum", "analytical thinking", "creativity", "adaptability"
            ]
        }

        # Flatten all skills for easy lookup
        self.all_skills = set()
        for category, skills in self.skill_keywords.items():
            self.all_skills.update(skill.lower() for skill in skills)

        # Common stop words
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }

    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-\+\#\.]', ' ', text)

        return text.strip()

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from text using simple keyword matching"""
        if not text:
            return {}

        preprocessed_text = self.preprocess_text(text)
        found_skills = {}

        for category, skills in self.skill_keywords.items():
            category_skills = []

            for skill in skills:
                # Create pattern for skill (word boundaries)
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'

                if re.search(pattern, preprocessed_text):
                    category_skills.append(skill)

            if category_skills:
                found_skills[category] = category_skills

        return found_skills

    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract important keywords from text"""
        if not text:
            return []

        # Preprocess text
        preprocessed = self.preprocess_text(text)

        # Simple tokenization (split by whitespace)
        tokens = preprocessed.split()

        # Remove stop words and short words
        filtered_tokens = [
            word for word in tokens
            if word not in self.stop_words
            and len(word) > 2
            and word.isalpha()
        ]

        # Count frequency
        word_freq = Counter(filtered_tokens)

        # Get most common words
        keywords = [word for word, _ in word_freq.most_common(max_keywords)]

        return keywords

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate basic text similarity using word overlap"""
        if not text1 or not text2:
            return 0.0

        # Preprocess both texts
        words1 = set(self.preprocess_text(text1).split())
        words2 = set(self.preprocess_text(text2).split())

        # Remove stop words
        words1 = {w for w in words1 if w not in self.stop_words and len(w) > 2}
        words2 = {w for w in words2 if w not in self.stop_words and len(w) > 2}

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def match_skills(self, resume_skills: Dict[str, List[str]], job_skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """Match skills between resume and job posting"""
        matched_skills = {}
        missing_skills = {}

        for category in job_skills:
            if category in resume_skills:
                resume_category_skills = set(skill.lower() for skill in resume_skills[category])
                job_category_skills = set(skill.lower() for skill in job_skills[category])

                matched = resume_category_skills.intersection(job_category_skills)
                missing = job_category_skills - resume_category_skills

                if matched:
                    matched_skills[category] = list(matched)
                if missing:
                    missing_skills[category] = list(missing)
            else:
                missing_skills[category] = job_skills[category]

        return {
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        }

    def calculate_match_score(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        """Calculate overall match score between resume and job"""

        # Extract skills from both texts
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_text)

        # Match skills
        skill_match = self.match_skills(resume_skills, job_skills)

        # Calculate text similarity
        text_similarity = self.calculate_text_similarity(resume_text, job_text)

        # Calculate skill match percentage
        total_job_skills = sum(len(skills) for skills in job_skills.values())
        total_matched_skills = sum(len(skills) for skills in skill_match["matched_skills"].values())

        skill_match_percentage = (total_matched_skills / max(total_job_skills, 1)) * 100

        # Calculate overall score (weighted combination)
        overall_score = (skill_match_percentage * 0.7) + (text_similarity * 100 * 0.3)

        return {
            "overall_score": min(overall_score, 100),
            "skill_match_percentage": skill_match_percentage,
            "text_similarity": text_similarity,
            "matched_skills": skill_match["matched_skills"],
            "missing_skills": skill_match["missing_skills"],
            "resume_skills": resume_skills,
            "job_skills": job_skills
        }

    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information from text"""
        contact_info = {
            "emails": [],
            "phones": [],
            "urls": []
        }

        if not text:
            return contact_info

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info["emails"] = list(set(emails))

        # Phone pattern
        phone_pattern = r'[\+]?[1-9]?[\d]{1,4}[\s\-\(\)]?[\d]{1,3}[\s\-\(\)]?[\d]{3,4}[\s\-]?[\d]{4}'
        phones = re.findall(phone_pattern, text)
        contact_info["phones"] = list(set(phones))

        # URL pattern
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        contact_info["urls"] = list(set(urls))

        return contact_info

# Global instance
basic_nlp_service = BasicNLPService()