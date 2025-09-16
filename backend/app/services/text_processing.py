import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import docx
import PyPDF2

class TextProcessingService:
    """Base text processing service for resume and job posting analysis"""

    def __init__(self):
        # Common skill categories for basic extraction
        self.skill_patterns = {
            "programming_languages": [
                r"\b(?:python|java|javascript|typescript|c\+\+|c#|php|ruby|go|rust|swift|kotlin)\b",
                r"\b(?:html|css|sql|r|matlab|scala|perl|dart|clojure)\b"
            ],
            "frameworks": [
                r"\b(?:react|angular|vue|django|flask|spring|express|laravel|rails)\b",
                r"\b(?:bootstrap|tailwind|jquery|node\.js|next\.js|nuxt\.js)\b"
            ],
            "databases": [
                r"\b(?:mysql|postgresql|mongodb|redis|elasticsearch|sqlite|oracle)\b",
                r"\b(?:cassandra|dynamodb|firebase|neo4j)\b"
            ],
            "cloud_platforms": [
                r"\b(?:aws|azure|gcp|google cloud|digital ocean|heroku|vercel)\b",
                r"\b(?:docker|kubernetes|terraform|jenkins)\b"
            ],
            "tools": [
                r"\b(?:git|github|gitlab|jira|confluence|slack|figma|photoshop)\b",
                r"\b(?:linux|ubuntu|windows|macos|bash|powershell)\b"
            ]
        }

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        try:
            if extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif extension in ['.docx', '.doc']:
                return self._extract_from_docx(file_path)
            elif extension == '.txt':
                return self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file format: {extension}")
        except Exception as e:
            raise Exception(f"Failed to extract text from {file_path}: {str(e)}")

    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _extract_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\(\)\-\@\+\#]', ' ', text)
        # Normalize to lowercase for processing
        return text.strip().lower()

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from text using pattern matching"""
        cleaned_text = self.clean_text(text)
        extracted_skills = {}

        for category, patterns in self.skill_patterns.items():
            skills = []
            for pattern in patterns:
                matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
                skills.extend([match.strip() for match in matches])

            # Remove duplicates while preserving order
            extracted_skills[category] = list(dict.fromkeys(skills))

        return extracted_skills

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information from text"""
        contact_info = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "website": None
        }

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info["email"] = email_match.group()

        # Phone pattern (various formats)
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info["phone"] = phone_match.group()

        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact_info["linkedin"] = "https://" + linkedin_match.group()

        # Website pattern
        website_pattern = r'https?://(?:www\.)?[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}'
        website_match = re.search(website_pattern, text)
        if website_match and "linkedin" not in website_match.group().lower():
            contact_info["website"] = website_match.group()

        return contact_info

    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """Extract important keywords from text"""
        cleaned_text = self.clean_text(text)

        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must'
        }

        words = re.findall(r'\b\w+\b', cleaned_text)
        keywords = []

        for word in words:
            if (len(word) >= min_length and
                word.lower() not in stop_words and
                not word.isdigit()):
                keywords.append(word.lower())

        # Return unique keywords with frequency
        keyword_freq = {}
        for keyword in keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1

        # Sort by frequency and return top keywords
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, freq in sorted_keywords[:50]]  # Top 50 keywords

    def calculate_keyword_density(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density for given keywords"""
        cleaned_text = self.clean_text(text)
        total_words = len(re.findall(r'\b\w+\b', cleaned_text))

        if total_words == 0:
            return {}

        density = {}
        for keyword in keywords:
            count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', cleaned_text))
            density[keyword] = (count / total_words) * 100

        return density

# Global instance
text_processing_service = TextProcessingService()