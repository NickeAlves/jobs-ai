from __future__ import annotations

from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from jobs_ai.config import get_settings
from jobs_ai.db import Database
from jobs_ai.resume import ResumeStore
from jobs_ai.workflow import ApplicationWorkflow


settings = get_settings()
db = Database(settings.app_database_path)
resume_store = ResumeStore(settings.app_resume_path, settings.app_cv_directory)
workflow = ApplicationWorkflow(settings, db, resume_store)

app = FastAPI(title="Jobs AI", version="0.1.0")
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class SearchRequest(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    limit: Optional[int] = None


class ResumeRequest(BaseModel):
    content: str


class AutoDiscoverRequest(BaseModel):
    limit: Optional[int] = None


class ChatRequest(BaseModel):
    message: str


class PlatformConnectionRequest(BaseModel):
    username: str = ""
    password: Optional[str] = None
    search_enabled: bool = True
    apply_enabled: bool = False
    notes: str = ""


@app.on_event("startup")
def on_startup() -> None:
    db.initialize()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/api/dashboard")
def dashboard() -> dict:
    return {
        "stats": db.stats(),
        "jobs": db.list_jobs(),
        "logs": db.list_logs(limit=200),
        "settings": {
            "require_manual_review": settings.app_require_manual_review,
            "auto_submit_enabled": settings.app_auto_submit_enabled,
            "resume_path": str(settings.app_resume_path),
            "cv_directory": str(settings.app_cv_directory),
            "default_query": settings.job_search_query,
            "default_location": settings.job_search_location,
            "default_limit": settings.job_search_limit,
        },
        "platforms": db.list_platform_connections(),
    }


@app.get("/api/jobs/{job_id}")
def get_job(job_id: int):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/api/jobs/search")
async def search_jobs(request: SearchRequest) -> dict:
    jobs = await workflow.search_jobs(request.query, request.location, request.limit)
    return {"jobs": jobs, "stats": db.stats(), "logs": db.list_logs(limit=200)}


@app.post("/api/jobs/auto-discover")
async def auto_discover_jobs(request: AutoDiscoverRequest) -> dict:
    try:
        jobs = await workflow.auto_discover_jobs(request.limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"jobs": jobs, "stats": db.stats(), "logs": db.list_logs(limit=200)}


@app.post("/api/jobs/{job_id}/analyze")
async def analyze_job(job_id: int):
    try:
        job = await workflow.analyze_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"job": job, "stats": db.stats(), "logs": db.list_logs(limit=200)}


@app.post("/api/jobs/{job_id}/submit")
async def submit_job(job_id: int):
    try:
        job = await workflow.submit_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"job": job, "stats": db.stats(), "logs": db.list_logs(limit=200)}


@app.post("/api/jobs/{job_id}/skip")
def skip_job(job_id: int):
    try:
        job = workflow.skip_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"job": job, "stats": db.stats(), "logs": db.list_logs(limit=200)}


@app.get("/api/resume")
def get_resume() -> dict:
    documents = resume_store.read_documents()
    return {
        "content": resume_store.read(),
        "path": str(settings.app_resume_path),
        "cv_directory": str(settings.app_cv_directory),
        "documents": [
            {"name": document.name, "path": document.path, "language": document.language}
            for document in documents
        ],
    }


@app.post("/api/resume")
def save_resume(request: ResumeRequest) -> dict:
    resume_store.write(request.content)
    db.add_log("info", "resume_saved", "Resume content updated.")
    return get_resume()


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict:
    try:
        answer = workflow.chat_with_lucai(request.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"agent": "LucAI", "answer": answer, "logs": db.list_logs(limit=200)}


@app.get("/api/platforms")
def list_platforms() -> dict:
    return {"platforms": db.list_platform_connections()}


@app.post("/api/platforms/{platform}")
def save_platform(platform: str, request: PlatformConnectionRequest) -> dict:
    known = {connection.platform for connection in db.list_platform_connections()}
    if platform not in known:
        raise HTTPException(status_code=404, detail="Platform not found")
    connection = db.save_platform_connection(
        platform=platform,
        username=request.username,
        password=request.password,
        search_enabled=request.search_enabled,
        apply_enabled=request.apply_enabled,
        notes=request.notes,
    )
    db.add_log(
        "info",
        "platform_connection_saved",
        f"{connection.display_name} connection settings updated.",
        metadata={
            "platform": connection.platform,
            "search_enabled": connection.search_enabled,
            "apply_enabled": connection.apply_enabled,
            "status": connection.status,
        },
    )
    return {"platform": connection, "platforms": db.list_platform_connections()}


def run() -> None:
    uvicorn.run("jobs_ai.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()
