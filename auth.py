import os
from datetime import datetime, timedelta
from typing import Dict

import jwt
import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import database

load_dotenv()

security = HTTPBearer()


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(data: Dict[str, str]) -> str:
    secret = os.getenv("APP_SECRET_KEY", "dev-secret")
    minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    payload = dict(data)
    payload["exp"] = datetime.utcnow() + timedelta(minutes=minutes)
    return jwt.encode(payload, secret, algorithm="HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, str]:
    secret = os.getenv("APP_SECRET_KEY", "dev-secret")
    try:
        payload = jwt.decode(credentials.credentials, secret, algorithms=["HS256"])
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    user = database.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"email": user["email"], "name": user["name"]}
