from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.integrations import router as integration_router
from backend.app.api.assessments import router as assessment_router

app = FastAPI(
    title="Module Integration Risk Assessment System",
    description="Module Integration Observability and Security Assessment",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(integration_router)
app.include_router(assessment_router)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_FILE = PROJECT_ROOT / "frontend" / "index.html"


@app.get("/", include_in_schema=False)
def dashboard():
    if DASHBOARD_FILE.exists():
        return FileResponse(DASHBOARD_FILE)
    return {
        "system": "Module Integration Risk Assessment System",
        "status": "running",
        "message": "Dashboard file not found",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
