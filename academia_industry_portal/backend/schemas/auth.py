from typing import Literal

from sqlmodel import SQLModel


class LoginRequest(SQLModel):
    email: str
    password: str
    role: Literal["student", "company"]


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUser(SQLModel):
    id: int
    role: Literal["student", "company"]
    email: str
