import re
import string
from typing import Dict, List, Any, Set
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class SimpleNLPService:
    """Simplified NLP service without spaCy dependency"""

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

        # Comprehensive skill taxonomy
        self.skill_taxonomy = {
            "programming_languages": {
                "python": ["python", "django", "flask", "fastapi", "pandas", "numpy", "scipy"],
                "javascript": ["javascript", "js", "node.js", "nodejs", "react", "vue", "angular", "typescript"],
                "java": ["java", "spring", "hibernate", "maven", "gradle"],
                "csharp": ["c#", "csharp", ".net", "dotnet", "asp.net"],
                "cpp": ["c++", "cpp", "cplusplus"],
                "php": ["php", "laravel", "symfony", "wordpress"],
                "ruby": ["ruby", "rails", "ruby on rails"],
                "go": ["go", "golang"],
                "rust": ["rust"],
                "kotlin": ["kotlin"],
                "swift": ["swift", "ios"],
                "r": ["r", "rstudio"],
                "matlab": ["matlab", "simulink"],
                "scala": ["scala", "akka"],
                "perl": ["perl"],
                "shell": ["bash", "shell", "powershell", "zsh"]
            },
            "databases": {
                "relational": ["mysql", "postgresql", "sqlite", "oracle", "sql server", "mariadb"],
                "nosql": ["mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "couchdb"],
                "graph": ["neo4j", "amazon neptune"],
                "analytics": ["bigquery", "redshift", "snowflake", "databricks"]
            },
            "cloud_platforms": {
                "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "cloudfront", "rds"],
                "azure": ["azure", "microsoft azure", "azure functions", "azure sql"],
                "gcp": ["google cloud", "gcp", "google cloud platform", "compute engine"],
                "other": ["heroku", "digitalocean", "linode", "vultr"]
            },
            "devops_tools": {
                "containerization": ["docker", "kubernetes", "k8s", "podman", "containerd"],
                "ci_cd": ["jenkins", "github actions", "gitlab ci", "travis ci", "circleci", "azure devops"],
                "infrastructure": ["terraform", "ansible", "puppet", "chef", "cloudformation"],
                "monitoring": ["prometheus", "grafana", "elk", "splunk", "datadog", "new relic"]
            },
            "web_technologies": {
                "frontend": ["html", "css", "sass", "less", "bootstrap", "tailwind", "material-ui"],
                "backend": ["rest", "graphql", "grpc", "soap", "microservices"],
                "frameworks": ["express", "koa", "fastify", "gin", "fiber"]
            },
            "data_science": {
                "ml_frameworks": ["tensorflow", "pytorch", "keras", "scikit-learn", "xgboost", "lightgbm"],
                "data_processing": ["pandas", "numpy", "dask", "spark", "hadoop"],
                "visualization": ["matplotlib", "seaborn", "plotly", "tableau", "power bi"],
                "statistics": ["statistics", "probability", "hypothesis testing", "regression"]
            },
            "soft_skills": {
                "communication": ["communication", "presentation", "writing", "documentation"],
                "leadership": ["leadership", "team management", "mentoring", "coaching"],
                "collaboration": ["teamwork", "collaboration", "agile", "scrum", "kanban"],
                "problem_solving": ["problem solving", "analytical thinking", "debugging", "troubleshooting"]
            }
        }

        # Flatten skills for easy lookup
        self.all_skills = {}
        for category, subcategories in self.skill_taxonomy.items():
            for subcategory, skills in subcategories.items():
                for skill in skills:
                    self.all_skills[skill.lower()] = {
                        "category": category,
                        "subcategory": subcategory,
                        "canonical": skills[0]  # First item is canonical form
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
        """Extract skills from text using pattern matching"""
        if not text:
            return {}

        preprocessed_text = self.preprocess_text(text)
        found_skills = {}

        # Look for skills in the text
        for skill, info in self.all_skills.items():
            # Create pattern for skill (word boundaries)
            pattern = r'\b' + re.escape(skill) + r'\b'

            if re.search(pattern, preprocessed_text):
                category = info["category"]
                if category not in found_skills:
                    found_skills[category] = []

                canonical_skill = info["canonical"]
                if canonical_skill not in found_skills[category]:
                    found_skills[category].append(canonical_skill)

        return found_skills

    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract important keywords from text"""
        if not text:
            return []

        # Preprocess text
        preprocessed = self.preprocess_text(text)

        # Tokenize
        tokens = word_tokenize(preprocessed)

        # Remove stopwords and short words
        filtered_tokens = [
            word for word in tokens
            if word.lower() not in self.stop_words
            and len(word) > 2
            and word.isalpha()
        ]

        # Count frequency
        word_freq = Counter(filtered_tokens)

        # Get most common words
        keywords = [word for word, _ in word_freq.most_common(max_keywords)]

        return keywords

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity"""
        if not text1 or not text2:
            return 0.0

        try:
            # Preprocess texts
            processed_text1 = self.preprocess_text(text1)
            processed_text2 = self.preprocess_text(text2)

            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=1000
            )

            tfidf_matrix = vectorizer.fit_transform([processed_text1, processed_text2])

            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            return float(similarity)

        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

    def analyze_keyword_density(self, text: str, target_keywords: List[str]) -> Dict[str, float]:
        """Analyze keyword density in text"""
        if not text or not target_keywords:
            return {}

        preprocessed = self.preprocess_text(text)
        tokens = word_tokenize(preprocessed)
        total_words = len(tokens)

        if total_words == 0:
            return {}

        keyword_counts = {}
        for keyword in target_keywords:
            # Count occurrences of keyword
            keyword_lower = keyword.lower()
            count = preprocessed.count(keyword_lower)
            density = (count / total_words) * 100
            keyword_counts[keyword] = density

        return keyword_counts

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
        text_similarity = self.calculate_similarity(resume_text, job_text)

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

# Global instance
simple_nlp_service = SimpleNLPService()