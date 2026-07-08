from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    name: str
    email: str


class AnalysisResult(BaseModel):
    id: Optional[str] = None
    resume_filename: str
    ats_score: int
    job_match_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    recommended_skills: List[str]
    strengths: List[str]
    improvements: List[str]
    better_wording: List[str]
    summary: str
    created_at: datetime
