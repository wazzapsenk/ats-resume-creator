from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, resume, analysis, latex, job_posting, upload
from app.core.config import settings

app = FastAPI(
    title="ATS Resume Creator API",
    description="API for ATS-optimized resume creation and analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(job_posting.router, prefix="/api/job-posting", tags=["job-posting"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(latex.router, prefix="/api/latex", tags=["latex"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])

@app.get("/")
async def root():
    return {"message": "ATS Resume Creator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}