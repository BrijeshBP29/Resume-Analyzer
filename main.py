from datetime import datetime
from pathlib import Path
from typing import Dict
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo.errors import DuplicateKeyError

from app.analyzer import analyze_resume
from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import database
from app.models import TokenResponse, UserCreate, UserLogin
from app.resume_parser import extract_text_from_pdf

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
UPLOAD_DIR = PROJECT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="AI Resume Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/dashboard")
def dashboard_page():
    return FileResponse(BASE_DIR / "static" / "dashboard.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "database": "memory" if database.using_memory else "mongodb"}


@app.post("/api/auth/signup", response_model=TokenResponse)
def signup(user: UserCreate):
    existing = database.users.find_one({"email": user.email.lower()})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    document = {
        "name": user.name,
        "email": user.email.lower(),
        "password_hash": hash_password(user.password),
        "created_at": datetime.utcnow(),
    }
    try:
        database.users.insert_one(document)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Email already registered") from exc

    token = create_access_token({"email": document["email"]})
    return TokenResponse(access_token=token, name=document["name"], email=document["email"])


@app.post("/api/auth/login", response_model=TokenResponse)
def login(user: UserLogin):
    document = database.users.find_one({"email": user.email.lower()})
    if not document or not verify_password(user.password, document["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"email": document["email"]})
    return TokenResponse(access_token=token, name=document["name"], email=document["email"])


@app.post("/api/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    current_user: Dict[str, str] = Depends(get_current_user),
):
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume")
    if len(job_description.strip()) < 30:
        raise HTTPException(status_code=400, detail="Job description is too short")

    safe_name = f"{uuid4()}-{Path(resume.filename).name}"
    file_path = UPLOAD_DIR / safe_name
    content = await resume.read()
    file_path.write_bytes(content)

    resume_text = extract_text_from_pdf(str(file_path))
    if not resume_text:
        raise HTTPException(status_code=422, detail="Could not extract text from this PDF")

    result = analyze_resume(resume_text, job_description)
    document = {
        **result,
        "user_email": current_user["email"],
        "resume_filename": resume.filename,
        "resume_text_preview": resume_text[:1200],
        "job_description_preview": job_description[:1200],
        "created_at": datetime.utcnow(),
    }
    inserted = database.analyses.insert_one(document)
    document["id"] = str(inserted.inserted_id)
    document.pop("_id", None)
    return document


@app.get("/api/analyses")
def list_analyses(current_user: Dict[str, str] = Depends(get_current_user)):
    rows = database.analyses.find({"user_email": current_user["email"]}).sort("created_at", -1)
    analyses = []
    for row in rows:
        row["id"] = str(row.get("_id"))
        row.pop("_id", None)
        analyses.append(row)
    return {"analyses": analyses}

