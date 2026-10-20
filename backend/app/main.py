from fastapi import FastAPI

from backend.app.api.integrations import router as integration_router


app = FastAPI(
    title="Module Integration Risk Assessment System",
    description="Stage 1 - Integration Observability and Security Data Collection",
    version="0.1.0",
)


app.include_router(integration_router)


@app.get("/")
def root():
    return {
        "system": "Module Integration Risk Assessment System",
        "stage": 1,
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
from backend.app.api.assessments import router as assessment_router
app.include_router(assessment_router)
