import os
import subprocess
import tempfile
import shutil
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import json
import logging
from datetime import datetime
from .pdf_cache import pdf_cache

logger = logging.getLogger(__name__)

class LaTeXService:
    """Service for generating PDF resumes using LaTeX templates"""

    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent.parent.parent / "latex-templates"
        self.output_dir = Path(__file__).parent.parent.parent / "temp" / "pdfs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Available templates
        self.available_templates = self._discover_templates()

    def _discover_templates(self) -> Dict[str, Dict[str, Any]]:
        """Discover available LaTeX templates"""
        templates = {}

        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return templates

        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir():
                template_file = template_dir / "template.tex"
                config_file = template_dir / "config.json"

                if template_file.exists():
                    config = {}
                    if config_file.exists():
                        try:
                            with open(config_file, 'r', encoding='utf-8') as f:
                                config = json.load(f)
                        except Exception as e:
                            logger.warning(f"Failed to load config for {template_dir.name}: {e}")

                    templates[template_dir.name] = {
                        "name": config.get("name", template_dir.name.title()),
                        "description": config.get("description", f"{template_dir.name} template"),
                        "style": config.get("style", "modern"),
                        "ats_optimized": config.get("ats_optimized", True),
                        "supports_photo": config.get("supports_photo", True),
                        "template_path": str(template_file.relative_to(self.templates_dir)),
                        "preview_image": config.get("preview_image", f"{template_dir.name}/preview.png")
                    }

        return templates

    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available templates"""
        return [
            {
                "id": template_id,
                **template_info
            }
            for template_id, template_info in self.available_templates.items()
        ]

    def generate_pdf(
        self,
        resume_data: Dict[str, Any],
        template_id: str = "modern",
        output_filename: Optional[str] = None,
        use_cache: bool = True
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Generate PDF from resume data using specified template

        Args:
            resume_data: Resume data dictionary
            template_id: Template identifier
            output_filename: Optional output filename
            use_cache: Whether to use caching (default: True)

        Returns:
            Tuple of (success: bool, message: str, pdf_path: Optional[str])
        """
        try:
            # Validate template
            if template_id not in self.available_templates:
                return False, f"Template '{template_id}' not found", None

            # Check cache first if enabled
            if use_cache:
                cached_pdf = pdf_cache.get_cached_pdf(resume_data, template_id)
                if cached_pdf:
                    # Copy cached file to output location
                    output_name = output_filename or f"resume_{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    output_path = self.output_dir / f"{output_name}.pdf"

                    try:
                        shutil.copy2(cached_pdf, str(output_path))
                        logger.info(f"PDF served from cache: {output_path}")
                        return True, "PDF generated from cache", str(output_path)
                    except Exception as e:
                        logger.warning(f"Failed to copy cached PDF: {e}")
                        # Continue with normal generation

            template_info = self.available_templates[template_id]
            template_path = template_info["template_path"]

            # Prepare resume data
            processed_data = self._prepare_resume_data(resume_data)

            # Render LaTeX template
            try:
                template = self.jinja_env.get_template(template_path)
                latex_content = template.render(**processed_data)
            except TemplateNotFound:
                return False, f"Template file not found: {template_path}", None
            except Exception as e:
                return False, f"Template rendering failed: {str(e)}", None

            # Generate PDF
            pdf_path = self._compile_latex_to_pdf(
                latex_content,
                output_filename or f"resume_{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            if pdf_path:
                # Cache the generated PDF if caching is enabled
                if use_cache:
                    try:
                        pdf_cache.cache_pdf(resume_data, template_id, str(pdf_path))
                    except Exception as e:
                        logger.warning(f"Failed to cache PDF: {e}")

                return True, "PDF generated successfully", str(pdf_path)
            else:
                return False, "PDF compilation failed", None

        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            return False, f"PDF generation error: {str(e)}", None

    def _prepare_resume_data(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and sanitize resume data for LaTeX rendering"""

        # Helper function to escape LaTeX special characters
        def escape_latex(text: str) -> str:
            if not isinstance(text, str):
                text = str(text)

            # LaTeX special characters that need escaping
            latex_chars = {
                '&': r'\&',
                '%': r'\%',
                '$': r'\$',
                '#': r'\#',
                '^': r'\textasciicircum{}',
                '_': r'\_',
                '{': r'\{',
                '}': r'\}',
                '~': r'\textasciitilde{}',
                '\\': r'\textbackslash{}'
            }

            for char, escaped in latex_chars.items():
                text = text.replace(char, escaped)

            return text

        # Helper function to format dates
        def format_date(date_str: str) -> str:
            if not date_str:
                return ""
            try:
                # Try different date formats
                for fmt in ["%Y-%m-%d", "%Y-%m", "%Y", "%m/%d/%Y", "%d/%m/%Y"]:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        return date_obj.strftime("%b %Y") if fmt in ["%Y-%m-%d", "%Y-%m"] else date_str
                    except ValueError:
                        continue
                return date_str
            except:
                return date_str

        # Process personal information
        processed = {
            "first_name": escape_latex(resume_data.get("first_name", "")),
            "last_name": escape_latex(resume_data.get("last_name", "")),
            "title": escape_latex(resume_data.get("title", "")),
            "email": resume_data.get("email", ""),  # Don't escape email
            "phone": resume_data.get("phone", ""),  # Don't escape phone
            "website": resume_data.get("website", ""),  # Don't escape URL
            "linkedin": resume_data.get("linkedin", ""),  # Don't escape URL
            "address": escape_latex(resume_data.get("address", "")),
            "summary": escape_latex(resume_data.get("summary", "")),
            "photo": resume_data.get("photo", "")  # Don't escape file path
        }

        # Process work experience
        work_experience = []
        for exp in resume_data.get("work_experience", []):
            if isinstance(exp, dict):
                processed_exp = {
                    "position": escape_latex(exp.get("position", "")),
                    "company": escape_latex(exp.get("company", "")),
                    "location": escape_latex(exp.get("location", "")),
                    "start_date": format_date(exp.get("start_date", "")),
                    "end_date": format_date(exp.get("end_date", "")),
                    "current": exp.get("current", False),
                    "description": escape_latex(exp.get("description", "")),
                    "achievements": [escape_latex(ach) for ach in exp.get("achievements", [])]
                }
                work_experience.append(processed_exp)

        processed["work_experience"] = work_experience

        # Process education
        education = []
        for edu in resume_data.get("education", []):
            if isinstance(edu, dict):
                processed_edu = {
                    "degree": escape_latex(edu.get("degree", "")),
                    "institution": escape_latex(edu.get("institution", "")),
                    "location": escape_latex(edu.get("location", "")),
                    "start_date": format_date(edu.get("start_date", "")),
                    "end_date": format_date(edu.get("end_date", "")),
                    "gpa": edu.get("gpa", ""),
                    "description": escape_latex(edu.get("description", "")),
                    "coursework": [escape_latex(course) for course in edu.get("coursework", [])]
                }
                education.append(processed_edu)

        processed["education"] = education

        # Process skills
        skills = []
        for skill in resume_data.get("skills", []):
            if isinstance(skill, dict):
                processed_skill = {
                    "category": escape_latex(skill.get("category", "")),
                    "items": skill.get("items", [])
                }
                # Handle both string and list formats for items
                if isinstance(processed_skill["items"], str):
                    processed_skill["items"] = escape_latex(processed_skill["items"])
                else:
                    processed_skill["items"] = [escape_latex(item) for item in processed_skill["items"]]

                skills.append(processed_skill)

        processed["skills"] = skills

        # Process projects
        projects = []
        for proj in resume_data.get("projects", []):
            if isinstance(proj, dict):
                processed_proj = {
                    "name": escape_latex(proj.get("name", "")),
                    "url": proj.get("url", ""),  # Don't escape URL
                    "description": escape_latex(proj.get("description", "")),
                    "technologies": proj.get("technologies", [])
                }
                # Handle both string and list formats for technologies
                if isinstance(processed_proj["technologies"], str):
                    processed_proj["technologies"] = escape_latex(processed_proj["technologies"])
                else:
                    processed_proj["technologies"] = [escape_latex(tech) for tech in processed_proj["technologies"]]

                projects.append(processed_proj)

        processed["projects"] = projects

        # Process certifications
        certifications = []
        for cert in resume_data.get("certifications", []):
            if isinstance(cert, dict):
                processed_cert = {
                    "name": escape_latex(cert.get("name", "")),
                    "issuer": escape_latex(cert.get("issuer", "")),
                    "date": format_date(cert.get("date", "")),
                    "credential_id": cert.get("credential_id", "")
                }
                certifications.append(processed_cert)

        processed["certifications"] = certifications

        # Process languages
        languages = []
        for lang in resume_data.get("languages", []):
            if isinstance(lang, dict):
                processed_lang = {
                    "language": escape_latex(lang.get("language", "")),
                    "proficiency": escape_latex(lang.get("proficiency", ""))
                }
                languages.append(processed_lang)

        processed["languages"] = languages

        # Process awards
        awards = []
        for award in resume_data.get("awards", []):
            if isinstance(award, dict):
                processed_award = {
                    "name": escape_latex(award.get("name", "")),
                    "issuer": escape_latex(award.get("issuer", "")),
                    "date": format_date(award.get("date", "")),
                    "description": escape_latex(award.get("description", ""))
                }
                awards.append(processed_award)

        processed["awards"] = awards

        return processed

    def _compile_latex_to_pdf(self, latex_content: str, filename: str) -> Optional[Path]:
        """Compile LaTeX content to PDF"""

        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Write LaTeX content to file
            tex_file = temp_path / f"{filename}.tex"
            try:
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(latex_content)
            except Exception as e:
                logger.error(f"Failed to write LaTeX file: {e}")
                return None

            # Copy template assets if they exist
            try:
                self._copy_template_assets(temp_path)
            except Exception as e:
                logger.warning(f"Failed to copy template assets: {e}")

            # Compile LaTeX to PDF
            try:
                # Run pdflatex twice to resolve references
                for _ in range(2):
                    result = subprocess.run([
                        'pdflatex',
                        '-interaction=nonstopmode',
                        '-output-directory', str(temp_path),
                        str(tex_file)
                    ], capture_output=True, text=True, cwd=temp_path)

                    if result.returncode != 0:
                        logger.error(f"pdflatex failed: {result.stderr}")
                        # Try to extract useful error information
                        if result.stdout:
                            logger.error(f"pdflatex stdout: {result.stdout}")
                        return None

                # Check if PDF was created
                pdf_file = temp_path / f"{filename}.pdf"
                if not pdf_file.exists():
                    logger.error("PDF file was not created")
                    return None

                # Copy PDF to output directory
                output_path = self.output_dir / f"{filename}.pdf"
                shutil.copy2(str(pdf_file), str(output_path))

                logger.info(f"PDF generated successfully: {output_path}")
                return output_path

            except FileNotFoundError:
                logger.error("pdflatex not found. Please install LaTeX distribution (TeX Live, MiKTeX, etc.)")
                return None
            except Exception as e:
                logger.error(f"PDF compilation failed: {e}")
                return None

    def _copy_template_assets(self, temp_dir: Path):
        """Copy template assets (images, fonts, etc.) to compilation directory"""

        # Copy common assets that might be referenced in templates
        assets_to_copy = [
            "images",
            "fonts",
            "styles",
            "assets"
        ]

        for template_id in self.available_templates:
            template_dir = self.templates_dir / template_id

            for asset_dir in assets_to_copy:
                source_asset_dir = template_dir / asset_dir
                if source_asset_dir.exists():
                    dest_asset_dir = temp_dir / asset_dir
                    try:
                        shutil.copytree(str(source_asset_dir), str(dest_asset_dir), dirs_exist_ok=True)
                    except Exception as e:
                        logger.warning(f"Failed to copy {asset_dir}: {e}")

    def validate_latex_installation(self) -> Tuple[bool, str]:
        """Validate that LaTeX is properly installed"""
        try:
            result = subprocess.run(['pdflatex', '--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return True, "LaTeX installation found"
            else:
                return False, "LaTeX installation not working properly"
        except FileNotFoundError:
            return False, "LaTeX not found. Please install TeX Live, MiKTeX, or similar"
        except Exception as e:
            return False, f"LaTeX validation error: {str(e)}"

    def preview_template(self, template_id: str) -> Optional[str]:
        """Get preview image path for template"""
        if template_id not in self.available_templates:
            return None

        template_info = self.available_templates[template_id]
        preview_path = self.templates_dir / template_info["preview_image"]

        if preview_path.exists():
            return str(preview_path)

        return None

    def get_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific template"""
        if template_id not in self.available_templates:
            return None

        return {
            "id": template_id,
            **self.available_templates[template_id]
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get PDF cache statistics"""
        return pdf_cache.get_cache_stats()

    def clear_cache(self):
        """Clear PDF cache"""
        pdf_cache.clear_cache()

# Global instance
latex_service = LaTeXService()