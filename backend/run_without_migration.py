#!/usr/bin/env python3
"""
Run the application without Alembic migration
Creates tables directly using SQLAlchemy
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import user, resume, job_posting, analysis

def create_tables():
    """Create all tables without migration"""
    try:
        # Import all models to ensure they're registered
        from app.models.user import User
        from app.models.resume import Resume
        from app.models.job_posting import JobPosting
        from app.models.analysis import Analysis

        # Create all tables
        user.Base.metadata.create_all(bind=engine)
        resume.Base.metadata.create_all(bind=engine)
        job_posting.Base.metadata.create_all(bind=engine)
        analysis.Base.metadata.create_all(bind=engine)

        print("✅ Database tables created successfully!")
        return True

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    if create_tables():
        print("🚀 You can now run: uvicorn app.main:app --reload --port 8000")
    else:
        print("💥 Fix the errors above and try again")