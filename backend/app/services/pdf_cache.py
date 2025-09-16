import os
import hashlib
import json
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import time
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Represents a cached PDF entry"""
    file_path: str
    created_at: float
    data_hash: str
    template_id: str
    file_size: int

class PDFCache:
    """Cache system for generated PDFs to improve performance"""

    def __init__(self, cache_dir: str = None, max_cache_size_mb: int = 100, max_age_hours: int = 24):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(__file__).parent.parent.parent / "temp" / "pdf_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self.max_age_seconds = max_age_hours * 3600

        # Cache metadata file
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.cache_metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, CacheEntry]:
        """Load cache metadata from disk"""
        if not self.metadata_file.exists():
            return {}

        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)

            # Convert to CacheEntry objects
            metadata = {}
            for key, entry_data in data.items():
                metadata[key] = CacheEntry(**entry_data)

            return metadata
        except Exception as e:
            logger.warning(f"Failed to load cache metadata: {e}")
            return {}

    def _save_metadata(self):
        """Save cache metadata to disk"""
        try:
            # Convert CacheEntry objects to dict
            data = {}
            for key, entry in self.cache_metadata.items():
                data[key] = {
                    'file_path': entry.file_path,
                    'created_at': entry.created_at,
                    'data_hash': entry.data_hash,
                    'template_id': entry.template_id,
                    'file_size': entry.file_size
                }

            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")

    def _generate_cache_key(self, resume_data: Dict[str, Any], template_id: str) -> str:
        """Generate a unique cache key for resume data and template"""
        # Create a deterministic hash from the resume data and template
        data_str = json.dumps(resume_data, sort_keys=True) + template_id
        return hashlib.md5(data_str.encode()).hexdigest()

    def _generate_data_hash(self, resume_data: Dict[str, Any]) -> str:
        """Generate a hash for the resume data only"""
        data_str = json.dumps(resume_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

    def get_cached_pdf(self, resume_data: Dict[str, Any], template_id: str) -> Optional[str]:
        """
        Get cached PDF path if it exists and is valid

        Returns:
            Path to cached PDF file if found, None otherwise
        """
        cache_key = self._generate_cache_key(resume_data, template_id)

        if cache_key not in self.cache_metadata:
            return None

        entry = self.cache_metadata[cache_key]
        file_path = Path(entry.file_path)

        # Check if file exists
        if not file_path.exists():
            logger.info(f"Cached file not found: {file_path}")
            self._remove_cache_entry(cache_key)
            return None

        # Check age
        age = time.time() - entry.created_at
        if age > self.max_age_seconds:
            logger.info(f"Cache entry expired: {cache_key}")
            self._remove_cache_entry(cache_key)
            return None

        # Verify data hasn't changed
        current_hash = self._generate_data_hash(resume_data)
        if current_hash != entry.data_hash:
            logger.info(f"Data changed, cache invalid: {cache_key}")
            self._remove_cache_entry(cache_key)
            return None

        logger.info(f"Cache hit: {cache_key}")
        return str(file_path)

    def cache_pdf(self, resume_data: Dict[str, Any], template_id: str, pdf_path: str) -> bool:
        """
        Cache a generated PDF

        Args:
            resume_data: The resume data used to generate the PDF
            template_id: The template ID used
            pdf_path: Path to the generated PDF file

        Returns:
            True if cached successfully, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(resume_data, template_id)
            source_path = Path(pdf_path)

            if not source_path.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                return False

            # Generate cache file path
            cache_filename = f"{cache_key}_{template_id}.pdf"
            cache_file_path = self.cache_dir / cache_filename

            # Copy file to cache
            import shutil
            shutil.copy2(str(source_path), str(cache_file_path))

            # Create cache entry
            file_size = cache_file_path.stat().st_size
            entry = CacheEntry(
                file_path=str(cache_file_path),
                created_at=time.time(),
                data_hash=self._generate_data_hash(resume_data),
                template_id=template_id,
                file_size=file_size
            )

            # Add to metadata
            self.cache_metadata[cache_key] = entry
            self._save_metadata()

            # Clean up old entries if needed
            self._cleanup_cache()

            logger.info(f"PDF cached: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to cache PDF: {e}")
            return False

    def _remove_cache_entry(self, cache_key: str):
        """Remove a cache entry and its file"""
        if cache_key not in self.cache_metadata:
            return

        entry = self.cache_metadata[cache_key]
        file_path = Path(entry.file_path)

        # Remove file
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to remove cached file {file_path}: {e}")

        # Remove from metadata
        del self.cache_metadata[cache_key]
        self._save_metadata()

    def _cleanup_cache(self):
        """Clean up old and oversized cache entries"""
        current_time = time.time()
        total_size = 0
        entries_by_age = []

        # Calculate total size and collect entries by age
        for cache_key, entry in self.cache_metadata.items():
            file_path = Path(entry.file_path)

            # Remove entries for missing files
            if not file_path.exists():
                self._remove_cache_entry(cache_key)
                continue

            # Remove expired entries
            age = current_time - entry.created_at
            if age > self.max_age_seconds:
                self._remove_cache_entry(cache_key)
                continue

            total_size += entry.file_size
            entries_by_age.append((cache_key, entry.created_at, entry.file_size))

        # Sort by age (oldest first)
        entries_by_age.sort(key=lambda x: x[1])

        # Remove oldest entries if over size limit
        while total_size > self.max_cache_size_bytes and entries_by_age:
            cache_key, _, file_size = entries_by_age.pop(0)
            self._remove_cache_entry(cache_key)
            total_size -= file_size
            logger.info(f"Removed old cache entry: {cache_key}")

    def clear_cache(self):
        """Clear all cached PDFs"""
        try:
            # Remove all cached files
            for cache_key in list(self.cache_metadata.keys()):
                self._remove_cache_entry(cache_key)

            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_files = len(self.cache_metadata)
        total_size = sum(entry.file_size for entry in self.cache_metadata.values())

        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "max_size_mb": round(self.max_cache_size_bytes / (1024 * 1024), 2),
            "max_age_hours": round(self.max_age_seconds / 3600, 1),
            "cache_dir": str(self.cache_dir)
        }

# Global cache instance
pdf_cache = PDFCache()