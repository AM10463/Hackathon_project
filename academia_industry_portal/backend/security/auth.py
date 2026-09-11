from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlmodel import Session

from database import get_session
from models.company import Company
from models.student import Student


password_hash = PasswordHash.recommended()
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-development-secret")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int, role: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=8)).timestamp()),
    }
    encoded_header = _encode_json(header)
    encoded_payload = _encode_json(payload)
    message = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_encode(signature)}"


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
        message = f"{encoded_header}.{encoded_payload}".encode()
        expected_signature = hmac.new(
            SECRET_KEY.encode(), message, hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_decode(encoded_signature), expected_signature):
            raise ValueError("Invalid token signature")
        payload = json.loads(_decode(encoded_payload))
        if payload["exp"] < datetime.now(timezone.utc).timestamp():
            raise ValueError("Expired token")
        user_id = int(payload["sub"])
        role = payload["role"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise credentials_error from error

    model = Student if role == "student" else Company if role == "company" else None
    user = session.get(model, user_id) if model else None
    if user is None:
        raise credentials_error
    return {"id": user_id, "role": role, "email": user.email, "user": user}


def require_role(role: str):
    def dependency(current_user=Depends(get_current_user)):
        if current_user["role"] != role:
            raise HTTPException(status_code=403, detail=f"{role.title()} role required")
        return current_user

    return dependency


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _encode_json(value: dict) -> str:
    return _encode(json.dumps(value, separators=(",", ":")).encode())
